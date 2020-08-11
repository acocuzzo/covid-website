import django.core.management
from projection.models import Parameter, Output
import datetime
from covid import *


def r0_range(start, stop):
    r0 = []
    for i in range(start, stop):
        if i == 0:
            r0.append(i)
        r0.append(float(i + 0.25))
        r0.append(float(i + .5))
        r0.append(float(i + .75))
        r0.append(float(i + 1))
    print('r0_range = ' + str(r0))
    return r0


def find_para(r0_opt, max_dur_opt, mult_opt):
    parameter_search = Parameter.objects.filter(
                            r0_value=r0_opt,
                            max_dur=max_dur_opt,
                            mult=mult_opt)
    if len(parameter_search) != 0:
        print('found model' + str(parameter_search[0]))
        return parameter_search[0]
    this_p = Parameter(
        r0_value=r0_opt,
        max_dur=max_dur_opt,
        mult=mult_opt)
    this_p.save()
    print('created new model: ' + str(this_p))
    return this_p


def find_output(parameter_set):
    output_search = Output.objects.filter(
            paramID=parameter_set).order_by('_day_since_zero')
    return output_search


def update_model(r0_opt, max_dur_opt, mult_opt):
    this_p = find_para(r0_opt, max_dur_opt, mult_opt)
    output = find_output(this_p)
    if len(output) != 0:
        print('found' + str(len(output)) + 'output entries')
    new_model = Model_30_set(r0_opt, max_dur_opt, mult_opt)
    print('ran model30_setter')
    # pass local model results to output objects
    # this can be multithreaded!
    new_model_size = Model_30_get_size(new_model)
    print('model has ' + str(new_model_size) + ' days')
    updated_output_count = 0
    new_output_count = 0
    for i in range(new_model_size):
        days_since = datetime.timedelta(days=i)
        this_date = this_p.day_zero + days_since
        # if there is prev output object, update
        if i <= len(output) - 1:
            output[i]._new_cases = (Model_30_get_cases(new_model, i))
            output[i]._date_updated = datetime.date.today()
            updated_output_count += 1
        # otherwise create new output object
        else:
            o = Output(
                paramID=this_p,
                _day=this_date,
                _day_since_zero=i,
                _new_cases=Model_30_get_cases(new_model, i),
                _date_updated= datetime.date.today())
            o.save()
            new_output_count += 1
    # update date
    print('updated ' + str(updated_output_count) + ' output entries')
    print('created ' + str(new_output_count) + ' new output entries')
    this_p.date_updated = datetime.date.today()
    print('date updated now ' + str(datetime.date.today()))
    this_p.save()
    print(str(this_p) + ' saved')


def update_models(r0_list, max_dur_list, mult_list):
    # update this to be multithreaded
    update_model_count = 0
    for r0_opt in r0_list:
        for max_dur_opt in max_dur_list:
            for mult_opt in mult_list:
                eliminate_duplicates(r0_opt, max_dur_opt, mult_opt)
                update_model(r0_opt, max_dur_opt, mult_opt)
                update_model_count += 1
    print(str(update_model_count) + 'models have been created/updated')


def eliminate_duplicates(r0_opt, max_dur_opt, mult_opt):
    parameter_search = Parameter.objects.filter(
                            r0_value=r0_opt,
                            max_dur=max_dur_opt,
                            mult=mult_opt)
    duplicates = 0
    if len(parameter_search) > 1:
        for i in range(1, len(parameter_search)):
            parameter_search[i].delete()
            duplicates += 1
        print('eliminated ' + str(duplicates) + 'duplicates')


def main():
    r0 = r0_range(0, 6)
    max_dur = [30, 45]
    mult = [0, 1, 2, 3]
    update_models(r0, max_dur, mult)

main()

