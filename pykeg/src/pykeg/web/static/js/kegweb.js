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
kegweb.API_GET_EVENTS_HTML = 'events/html/';
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
kegweb.getEventsHtml = function(callback, since) {
  var url = kegweb.API_BASE + kegweb.API_GET_EVENTS_HTML;
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
  if ($("#kb-recent-events")) {
    if (kegweb.lastEventId >= 0) {
      kegweb.getEventsHtml(kegweb.updateEventsTable, kegweb.lastEventId);
    } else {
      kegweb.getEventsHtml(kegweb.updateEventsTable);
    }
  }
}

/**
 * Updates the kb-recent-events table from a list of events.
 */
kegweb.updateEventsTable = function(events) {
  for (var rowId in events) {
    var row = events[rowId];
    var animate = kegweb.eventsLoaded;
    var eid = parseInt(row['id']);
    if (eid > kegweb.lastEventId) {
      kegweb.lastEventId = eid;
    }

    var newDivName = 'kb-event-' + row['id'];
    var newDiv = '<div id="' + newDivName + '">';
    newDiv += row['html'];
    newDiv += '</div>';

    newDivName = "#" + newDivName;
    $('#kb-recent-events').prepend(newDiv);
    $(newDivName).find("abbr.timeago").timeago();
    $(newDivName).find("span.hmeasure").autounits(kegweb.AUTOUNITS_SETTINGS);

    if (animate) {
      $(newDivName).css("display", "none");
      $(newDivName).css("background-color", "#ffc800");
      $(newDivName).show("slide", { direction: "up" }, 1000, function() {
          $(newDivName).animate({ backgroundColor: "#ffffff" }, 1500);
      });
    }
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

