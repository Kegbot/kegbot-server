/**
 * Copyright 2011 Mike Wakerly <opensource@hoho.com>
 *
 * This file is part of the Pykeg package of the Kegbot project.
 * For more information on Pykeg or Kegbot, see http://kegbot.org/
 *
 * Pykeg is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * Pykeg is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Pykeg.  If not, see <http://www.gnu.org/licenses/>.
 */

//
// Kegweb namespace setup
//
var kegweb = {};

// API Endpoints.
kegweb.API_BASE = '/api/';
kegweb.API_GET_EVENTS = 'events/';
kegweb.AUTOUNITS_SETTINGS = {};

//
// Kegweb functions.
//

kegweb.refreshDisplayUnits = function(useMetric) {
    var override = $.cookie("autounits_usemetric");
    if (override != null) {
        useMetric = (override == 'true');
    }
    kegweb.AUTOUNITS_SETTINGS['metric'] = useMetric;

    $("span.hmeasure").autounits(kegweb.AUTOUNITS_SETTINGS);

    var toggleBox = $("#units-selector");
    var text;
    if (useMetric) {
        text = "units: metric ";
        text += "(<a href='#' onClick='kegweb.overrideDisplayUnits(false);'>";
        text += "switch to imperial";
        text += "</a>)";
    } else {
        text = "units: imperial ";
        text += "(<a href='#' onClick='kegweb.overrideDisplayUnits(true);'>";
        text += "switch to metric";
        text += "</a>)";
    }
    toggleBox.html(text);
}

kegweb.overrideDisplayUnits = function(useMetric) {
    $.cookie("autounits_usemetric", useMetric, {
        path: '/'
    });
    kegweb.refreshDisplayUnits(useMetric);
}

$(function() {

    //
    // BACKBONE MODELS
    //
    var SystemEvent = Backbone.Model.extend({
        initialize: function(spec) {
            var title = "Unknown event.";
            var kind = spec.event.kind;
            if (kind == "drink_poured") {
                title = "poured a drink";
            } else if (kind == "session_joined") {
                title = "started drinking";
            } else if (kind == "session_started") {
                title = "started a new session";
            } else {
                title = "unknown event";
            }
            var username;
            if (spec.event.user_id) {
                username = spec.event.user_id;
            } else {
                username = "a guest";
            }
            this.set({
                kind: spec.event.kind,
                htmlId: 'systemevent_' + this.cid,
                eventTitle: title,
                eventUser: username,
            })
            this.set(spec);
			
            this.id = spec.event.id;
            this.cid = this.id;
        }
    });

    var SystemEventList = Backbone.Collection.extend({
        model: SystemEvent,

        url: function() {
            if (this.length == 0) {
                return "/api/events/";
            } else {
                return "/api/events/?since=" + this.last().id;
            }
        },

        comparator: function(e) {
            var evt = e.get("event");
            return e.get("event").id;
        },

        initialize: function() {
            this.lastEventId = -1;
            this.on("add", function(event) {
                console.log("Event added: " + event);
                var eventId = parseInt(event.id);
                if (eventId > this.lastEventId) {
                    this.lastEventId = eventId;
                }

                var kind = event.get("kind");
                if (kind == "session_started") {
                    var sessionId = event.get("event").session_id;
                    if (app.drinkingSessions.get(sessionId) == null) {
                        console.log("New session started: " + sessionId);
                    var ds = new DrinkingSession({
                        id: sessionId
                    });
                    ds.fetch();
                    app.drinkingSessions.add(ds);
                    }
                }
            }, this);
        },

        parse: function(response) {
            if ("events" in response.result) {
                return response.result.events;
            } else {
                return Array();
            }
        },
    });

    var DrinkingSession = Backbone.Model.extend({
        urlRoot: "/api/sessions/",

        initialize: function(spec) {
            this.id = spec.id;
            this.set(spec);
        }
    });

    var DrinkingSessionList = Backbone.Collection.extend({
        model: DrinkingSession,
        url: "/api/sessions/",

        initialize: function() {
            this.on("add", function(session) {
                console.log("Session added: " + session.get("id"));
            });
        },

        comparator: function(session) {
            return session.get("id");
        },

        parse: function(response) {
            if ("sessions" in response.result) {
                return response.result.sessions;
            } else {
                return Array();
            }
        },
    });

    //
    // BACKBONE VIEWS
    //
    var SystemEventView = Backbone.View.extend({
        render: function() {
            var kind = this.model.get('event').kind;
            switch (kind) {
            case "keg_tapped":
                this.setElement(ich.systemevent_keg_started(this.model.toJSON()));
                break;
            case "keg_ended":
                this.setElement(ich.systemevent_keg_ended(this.model.toJSON()));
                break;
            case "drink_poured":
                this.setElement(ich.systemevent_drink_poured(this.model.toJSON()));
                break;
            case "session_started":
            case "session_joined":
                this.setElement(ich.systemevent(this.model.toJSON()));
                break;
            default:
                break;
            }
            this.$("abbr.timeago").timeago();
            this.$("span.hmeasure").autounits(kegweb.AUTOUNITS_SETTINGS);

            var el = this.$el;
            el.css("display", "none");
            el.css("background-color", "#ffc800");
            el.show("slide", {
                direction: "up"
            }, 1000, function() {
                el.animate({
                    backgroundColor: "#ffffff"
                }, 1500);
            });

            return this;
        },
    });

    var SystemEventListView = Backbone.View.extend({
        //tagName: "div",
        //className: "kbSystemEvents",
        el: $("#kb-system-events"),

        initialize: function(options) {
            this.collection.bind("add", function(model) {
                var eventView = new SystemEventView({
                    model: model
                });
                $(this.el).prepend(eventView.render().el);
            }, this);
        },

        render: function() {
			console.log("Event list: render!");
            return this;
        }

    });

    //
    // BACKBONE APP
    //
    var KegwebAppModel = Backbone.Model.extend({
        initialize: function() {
            this.systemEvents = new SystemEventList();
            this.drinkingSessions = new DrinkingSessionList();
            this.eventListView = new SystemEventListView({
                collection: this.systemEvents
            });
			console.log("Kegbot app initialized!");
        }
    });
	
    window.app = new KegwebAppModel();
});
