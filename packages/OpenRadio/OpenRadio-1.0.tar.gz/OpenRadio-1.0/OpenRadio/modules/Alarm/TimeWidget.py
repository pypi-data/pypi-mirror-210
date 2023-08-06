from gi.repository import Gtk


class TimeWidget(Gtk.AspectFrame):
    def __init__(self, hours, minutes):
        Gtk.AspectFrame.__init__(
            self, label=_("Time"), xalign=0.5, yalign=0.5, obey_child=True
        )

        time_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        hours_button = Gtk.SpinButton.new_with_range(0, 23, 1)
        hours_button.set_orientation(Gtk.Orientation.VERTICAL)
        hours_button.set_name("hours")
        hours_button.set_value(hours)
        hours_button.set_size_request(125, 225)
        hours_button.set_wrap(True)

        hours_button.set_margin_left(10)
        hours_button.set_margin_right(10)
        hours_button.set_margin_bottom(10)
        hours_button.connect("output", self.show_zeros)

        minutes_button = Gtk.SpinButton.new_with_range(0, 59, 1)
        minutes_button.set_orientation(Gtk.Orientation.VERTICAL)
        minutes_button.set_name("minutes")
        minutes_button.set_value(minutes)
        minutes_button.set_size_request(125, 225)
        minutes_button.set_wrap(True)

        minutes_button.set_margin_left(10)
        minutes_button.set_margin_right(10)
        minutes_button.set_margin_bottom(10)
        minutes_button.connect("output", self.show_zeros)

        time_seperator = Gtk.Label(label=":")
        time_seperator.set_name("time_seperator")

        time_box.pack_start(hours_button, False, False, 2)
        time_box.pack_start(time_seperator, False, False, 2)
        time_box.pack_start(minutes_button, False, False, 2)

        self.add(time_box)

        self.hours_button = hours_button
        self.minutes_button = minutes_button

    def show_zeros(self, spinbutton):
        adjustment = spinbutton.get_adjustment()
        spinbutton.set_text("{:02d}".format(int(adjustment.get_value())))
        return True

    def get_minutes(self):
        return int(self.minutes_button.get_value())

    def get_hours(self):
        return int(self.hours_button.get_value())
