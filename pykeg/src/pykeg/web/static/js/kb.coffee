###
Copyright 2012 Mike Wakerly <opensource@hoho.com>

This file is part of the Pykeg package of the Kegbot project.
For more information on Pykeg or Kegbot, see http://kegbot.org/

Pykeg is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

Pykeg is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Pykeg.  If not, see <http://www.gnu.org/licenses/>.
###

## Constants

# Polling interval when there is an active session.
POLL_INTERVAL_ACTIVE_SESSION = 5 * 1000

# Polling interval when no session is active.
POLL_INTERVAL_NO_SESSION = 60 * 1000

## Models

SystemEvent = Backbone.Model.extend
    initialize: (spec) ->
        kind = spec.kind

        switch kind
            when "drink_poured" then title = "poured a drink"
            when "session_joined" then title = "started drinking"
            when "session_started" then title = "started a new session"
            else title = "unknown event"

        if spec.user_id then username = spec.user_id else username = "a guest"

        @id = spec.id
        @cid = this.id

        @set
            kind: kind
            htmlId: "systemevent_" + this.cid
            eventTitle: title
            eventUser: username
        @set spec

        return @


SystemEventView = Backbone.View.extend
    render: ->
        kind = @model.get("kind")

        switch kind
            when "keg_tapped"
                tmpl = ich.systemevent_keg_started
            when "keg_ended"
                tmpl = ich.systemevent_keg_ended
            when "drink_poured"
                tmpl = ich.systemevent_drink_poured
            when "session_started", "session_joined"
                tmpl = ich.systemevent

        if tmpl? then @setElement(tmpl(@model.toJSON()))
        @$("abbr.timeago").timeago()
        @$("span.hmeasure").autounits(metric:window.app.pageSettings.get('metric'))

        el = @$el
        el.show()
        #el.css "display", "none"
        #el.css "background-color", "#ffc800"
        #el.show "slide", direction:"up", 1000, ->
        #   el.animate backgroundColor:"#ffffff", 1500

        return @


SystemEventList = Backbone.Collection.extend
    model: SystemEvent

    initialize: ->
        @lastEventId = -1
        @on("add", (event) ->
            kind = event.get("kind")
            eventId = parseInt(event.id)
            console.log "Event added: id=" + eventId + " kind=" + kind

            if eventId >= @lastEventId
                @lastEventId = eventId

            if kind == "session_started"
                ds = new DrinkingSession(event.get("session"))
                if not app.drinkingSessions.get(ds.id)
                    app.drinkingSessions.add(ds)
                    ds.fetch(success: (session) ->
                        console.log("New session " + session.id + " loaded.")
                        app.drinkingSessions.add(session))

            return
        , @)
        return @

    url: ->
        if @length == 0
            return window.app.getApiBase() + "events/"
        else
            return window.app.getApiBase() + "events/?since=" + @last().id

    parse: (response) ->
        return response.objects

    comparator: (e) ->
        return e.id


SystemEventListView = Backbone.View.extend
    el: $("#kb-system-events")

    initialize: (options) ->
        @collection.bind("add", (model) ->
            @setElement($("#kb-system-events"))
            eventView = new SystemEventView model:model
            $(@el).prepend(eventView.render().el)
            return
        , @)
        return @

    render: ->
        console.log "Event list: render!"
        return @


DrinkingSession = Backbone.Model.extend
    urlRoot: ->
        return window.app.getApiBase() + "sessions/"

    initialize: (spec) ->
        @id = spec.id
        @set spec
        return @

    parse: (response) ->
        return response.object


DrinkingSessionList = Backbone.Collection.extend
    model: DrinkingSession
    url: ->
        return window.app.getApiBase() + "sessions/"

    initialize: ->
        @on "add", (session) ->
            console.log "Session added: " + session.get("id")
        return @

    comparator: (session) ->
        return session.get "id"

    parse: (response) ->
        return if "objects" in response then response.objects else []


PageSettings = Backbone.Model.extend
    initialize: (spec) ->
        @set metric:false
        @on("change:metric", (model) ->
            useMetric = @get("metric")
            $("span.hmeasure").autounits(metric:useMetric)
        , @)

    setMetric: (useMetric=true) ->
        @set metric:useMetric

    toggleMetric: ->
        @set metric:(not @get "metric")


PageSettingsView = Backbone.View.extend
    initialize: (options) ->
        @model.on("change:metric", (model) ->
            console.log "PageSettingsView: Settings changed"
            @render()
        , @)
        return @

    render: ->
        @setElement($("#page-settings"))
        if @model.get("metric")
            @$el.html("<small>(current: metric)</small>")
        else
            @$el.html("<small>(current: imperial)</small>")

## Main app

KegwebAppModel = Backbone.Model.extend
    initialize: (options) ->
        @systemEvents = new SystemEventList
        @drinkingSessions = new DrinkingSessionList
        @eventListView = new SystemEventListView collection:@systemEvents
        @pageSettings = new PageSettings
        @pageSettingsView = new PageSettingsView model:@pageSettings
        @set "pageSettings":@pageSettings
        @set "apiBase":"/api/"
        console.log "Kegbot app initialized!"
        return @

    setApiBase: (url) ->
        console.log "Api base URL set to " + url
        @set "apiBase":url

    getApiBase: ->
        return @get("apiBase")

    getPageSettings: ->
        return @get("pageSettings")

    refresh: ->
        # Reload latest system events.
        @systemEvents.fetch(add:true)
        have_active_session = false
        
        # Refresh each active session. (There should never be more than one.)
        @drinkingSessions.each((session) ->
            if session.get('is_active')
                have_active_session = true
                session.fetch()
        )
        update_fn = _.bind(@refresh, this)
        timeout = if have_active_session then POLL_INTERVAL_ACTIVE_SESSION else POLL_INTERVAL_NO_SESSION
        setTimeout(update_fn, timeout)

window.app = new KegwebAppModel