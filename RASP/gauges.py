from Tkinter import Canvas


class hybridGauge(Canvas):
    def __init__(self, window,color, value, maxVal, name, gaugeScale, lineColor, bgColor, textFont):
        Canvas.__init__(self, window, bg=bgColor, height=100, width=100)
        xval = 20
        yval = 10
        self.maxVal = maxVal
        self.value = value

        self.gaugeValue = self.maxVal / float(value)  # calculate the GaugeValue

        self.hand = self.create_arc(xval, yval, (xval + 100 * gaugeScale),
                                      (yval + 100 * gaugeScale), start=0,
                                      extent=-(220 / self.gaugeValue), fill=color)  # Draw hand

        self.outline = self.create_arc(xval - 3, yval - 3, (xval + 100 * gaugeScale + 3),
                                         (yval + 100 * gaugeScale + 3), start=0, extent=-220, style="arc",
                                         outline=lineColor, width=2)  # draw outline

        self.valueBox = self.create_rectangle((xval + 50 * gaugeScale), yval + 20 * gaugeScale,
                                                xval + 100 * gaugeScale + 3, yval + 50 * gaugeScale,
                                                outline=lineColor,
                                                width=2)  # draw Value Box

        self.value1 = self.create_text(xval + 54 * gaugeScale, yval + 22 * gaugeScale, anchor="nw",
                                         text=self.value,
                                         fill=lineColor, font=(textFont, int(round(15 * gaugeScale))))

        self.value2 = self.create_text(xval-10, yval - 8, anchor="nw", text=name, fill=lineColor,
                                         font=(textFont, int(round(19 * gaugeScale))))
    def updateval(self, valueUpdated):
        self.itemconfig(self.value1, text=valueUpdated)
        gaugeValue = self.maxVal / float(valueUpdated)
        self.itemconfig(self.hand, extent=-(220 / gaugeValue))

class digitalGauge(Canvas):
    def __init__(self, window,color, value,name, lineColor, bgColor, textFont):
        Canvas.__init__(self, window, bg=bgColor, height=100, width=100)
        xval = 20
        yval = 10

        self.value = value

        self.value1 = self.create_text(xval + 54, yval + 22, anchor="nw", text=name + " " + str(self.value), fill=lineColor,
                                       font=(textFont, int(round(15))))
    def updateval(self, valueUpdated):
        self.itemconfig(self.value1, text=valueUpdated)

