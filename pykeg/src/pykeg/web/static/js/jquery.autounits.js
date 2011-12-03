/*
 * autounits: a jQuery plugin, version: 0.1.0 (2011-08-27)
 * @requires jQuery v1.2.3 or later
 */
(function($) {

  $.fn.autounits = function(options) {
    var settings = {
      'metric': true,
      'humanize': true,
    };
    
    if (options) {
      $.extend(settings, options);
    }

    this.each(function() {
      refresh(settings, this);
    });
    return this;
  };

  function refresh(settings, self) {
    var data = prepareData(self);
    $(self).text(toHuman(settings, data.volume_ml));
    return this;
  }

  function prepareData(self) {
    var element = $(self);
    if (!element.data("autounits")) {
      var text = $.trim(element.text());
      element.data("autounits", {
        num: $(self).find("span.num").text(),
        unit: $(self).find("span.unit").text(),
        volume_ml: $(self).find("span.num").text(),
      });
    }
    return element.data("autounits");
  }

  function toOunces(amountInMilliliters) {
    return 0.0338140227 * amountInMilliliters;
  }

  function toHuman(settings, volume_ml) {
    volume_ml = parseFloat(volume_ml);

    if (!settings.metric) {
      var amt = toOunces(volume_ml);
      var units = "oz";
      if (amt > 8) {
        amt /= 16.0;
        units = "pints";
      }

      if (amt < 10) {
        amt = amt.toFixed(2);
      } else {
        amt = amt.toFixed(1);
      }

      return amt + " " + units;
    } else {
      var liters = volume_ml / 1000.0;
      if (liters < 0.5) {
        liters = liters.toFixed(2);
      } else {
        liters = liters.toFixed(1);
      }

      return liters + " L";
    }
  }

})(jQuery);
