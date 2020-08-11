from django.db import models
import datetime

import sys
sys.path.insert(0, '/home/anna/code/exercises/probability')

nyc_day_zero = datetime.date(2020, 2, 29)
maintenance = 21

class Parameter(models.Model):
    r0_value = models.DecimalField(max_digits=3, decimal_places=2, default=1.0)
    max_dur = models.PositiveSmallIntegerField(choices=((30, '30'), (45,
                                                                     '45')),
                                               default=45)
    cont_dur = models.PositiveSmallIntegerField(default=7)
    mult = models.PositiveSmallIntegerField(
        choices=((0, 'assume case accurate'), (1, 'multiply cases by 10'),
                 (2, 'death rate .01'), (3, 'death rate .02')),
        default=0)
    date_updated = models.DateField('date updated', null=True)
    time_updated = models.TimeField('time updated', null=True)
    day_zero = models.DateField('day zero', null=True, default=nyc_day_zero)
    model_size = models.IntegerField(null=True, default=0)

    def __str__(self):
        p_string = (str(self.r0_value) + "," + str(self.max_dur) + "," +
                    str(self.cont_dur) + "," + str(self.mult))
        return p_string

    def was_updated_today(self):
        this_hour = datetime.datetime.now().hour
        this_minute = datetime.datetime.now().minute
        one_day = datetime.timedelta(days=1)
        yesterday = datetime.date.today() - one_day
        if self.date_updated == yesterday and this_hour <= 20 and this_minute <= 45:
            return True
        return self.date_updated == datetime.date.today()


class Output(models.Model):
    paramID = models.ForeignKey(Parameter, on_delete=models.CASCADE)
    _day = models.DateField(null=True)
    _day_since_zero = models.PositiveSmallIntegerField(null=True)
    _date_updated = models.DateTimeField('date updated', null = True)
    _new_cases = models.PositiveIntegerField(null=True)
    _new_deaths = models.PositiveIntegerField(null=True)


    def __str__(self):
        o_string = ("Model: " + str(self.paramID.id) + ", days since day_zero: " + str(self._day_since_zero) + "," +
                " cases: " + str(self._new_cases) + ", deaths: " + str(self._new_deaths))
        return o_string

   
    def was_updated_today(self):
        this_hour = datetime.datetime.now().hour
        this_minute = datetime.datetime.now().minute
        one_day = datetime.timedelta(days=1)
        yesterday = datetime.date.today() - one_day
        if self.date_updated == yesterday and this_hour <= 20 and this_minute <= 45:
            return True
        return self.date_updated == datetime.date.today()
