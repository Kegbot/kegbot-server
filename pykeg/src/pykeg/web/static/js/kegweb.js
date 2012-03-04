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

// Misc globals.
kegweb.lastEventId = -1;
kegweb.eventsLoaded = false;

//
// Kegweb functions.
//

/**
 * Based Kegweb onRead function, called when any kegweb page is loaded.
 */
kegweb.onReady = function() {
  kegweb.refreshCallback();
  setInterval(kegweb.refreshCallback, 10000);
};

/**
 * Fetches the latest events in pre-processed HTML format.
 *
 * @param {function(Array)} callback A callback function to process the events.
 * @param {number} since Fetch only events that are newer than this event id.
 */
kegweb.getEvents = function(callback, since) {
  var url = kegweb.API_BASE + kegweb.API_GET_EVENTS;
  if (since) {
    url += '?since=' + since;
  }
  $.getJSON(url, function(data) {
    if (data['result'] && data['result']['events']) {
      callback(data['result']['events']);
    }
  });
}

/**
 * Interval callback that will refresh all items on the page.
 */
kegweb.refreshCallback = function() {
  // Events table.
  if ($("#kb-system-events")) {
    if (kegweb.lastEventId >= 0) {
      kegweb.getEvents(kegweb.updateEventsTable, kegweb.lastEventId);
    } else {
      kegweb.getEvents(kegweb.updateEventsTable);
    }
  }
}

/**
 * Updates the kb-recent-events table from a list of events.
 */
kegweb.updateEventsTable = function(events) {
  events.reverse();
  for (var rowId in events) {
    var row = events[rowId];
    var animate = kegweb.eventsLoaded;
    var eid = parseInt(row['event']['id']);
    if (eid > kegweb.lastEventId) {
      kegweb.lastEventId = eid;
    }

    var l = window.app.model.systemevents;
    var e = new SystemEvent(row);
    if (l.get(e.id)) {
      // Already in collection, grr.
    } else {
      l.add(e);
    }

    /*
    if (animate) {
    }
    */
  }
  if (!kegweb.eventsLoaded) {
    kegweb.eventsLoaded = true;
  }
}

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
  $.cookie("autounits_usemetric", useMetric, { path: '/' });
  kegweb.refreshDisplayUnits(useMetric);
}

var SystemEvent = Backbone.Model.extend({
  initialize: function (spec) {
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
      username = "guest";
    }
    this.set({
      id: spec.event.id,
      htmlId: 'systemevent_' + this.cid,
      eventTitle: title,
      eventUser: username,
    });

  }
});

var SystemEventView = Backbone.View.extend({
  render: function () {
    var kind = this.model.get('event').kind;
    switch (kind) {
      case "keg_tapped":
        this.setElement(ich.systemevent_keg_started(this.model.toJSON()));
        break;
      case "keg_ended":
        this.setElement(ich.systemevent_keg_ended(this.model.toJSON()));
        break;
      case "drink_poured":
      case "session_started":
      case "session_joined":
        this.setElement(ich.systemevent(this.model.toJSON()));
        break;
      default:
        break;
    }
    this.$("abbr.timeago").timeago();
    return this;
  },
});

var SystemEventList = Backbone.Collection.extend({
  model: SystemEvent,
  url: '/api/events',
  comparator: function (e) {
    var evt = e.get("event");
    return e.get("event").id;
  },
  initialize: function () {
    // TODO
  },
});

var KegwebAppModel = Backbone.Model.extend({
  initialize: function () {
    this.systemevents = new SystemEventList();
  }
});

var KegwebAppView = Backbone.View.extend({
  initialize: function() {
    _.bindAll(this, "addSystemEvent");
    this.model.systemevents.bind('add', this.addSystemEvent);
  },

  events: {
    // User events
  },

  render: function() {
    $(this.el).html(ich.systemevent_list(this.model.toJSON()));
    //$(this.el).html("here");
    this.eventList = this.$('#eventlist');
    return this;
  },

  addSystemEvent: function (systemEvent) {
    var view = new SystemEventView({model: systemEvent});
    var el = view.render().el;

    if (kegweb.eventsLoaded) {
      $(el).css("display", "none");
      $(el).css("background-color", "#ffc800");
      $(el).show("slide", { direction: "up" }, 1000, function() {
          $(el).animate({ backgroundColor: "#ffffff" }, 1500);
      });
    }

    this.eventList.prepend(el);
  },

});

var KegwebAppRouter = Backbone.Router.extend({
  initialize: function (params) {
    this.model = new KegwebAppModel({});
    this.view = new KegwebAppView({model: this.model});
    params.append_at.append(this.view.render().el);
    return this;
  },
});
