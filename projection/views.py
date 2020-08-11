from django.http import JsonResponse
from projection.models import Parameter, Output
import datetime
from covid import *
# from .models import Parameter, Output
from django.db import transaction
from django.shortcuts import render


def isMaintenance():
    this_hour = datetime.datetime.now().hour
    this_minute = datetime.datetime.now().minute
    return (this_hour == 20 and this_minute > 40) or this_hour == 21


def graph(request):
    return render(request, 'graph.html')


def graph_data(request):
    # get user input
    input_r0 = float(request.GET.get('r0_num'))
    input_max_dur = int(request.GET.get('max_dur'))
    input_mult = int(request.GET.get('mult'))
    error_mess = ''
    if input_r0 < 0:
        error_mess += 'r0 cannot be negative'
    if input_max_dur <= 0:
        error_mess += 'max_dur cannot be non-positive'
    if input_mult < 0 or input_mult > 3:
        error_mess += 'multiplier value error, defaulted to 0'
    output = get_output(
        get_para(input_r0, input_max_dur, input_mult),
        input_r0, input_max_dur, input_mult)
    main_mess = ''
    if isMaintenance():
        main_mess = 'Database currently being updated, models reflect NYC Gov Data as of prior to 9:30pm EST'
    csv_json = {
        'input_r0': input_r0,
        'input_max_dur': input_max_dur,
        'input_mult': input_mult,
        'csv_string': output,
        'maintenance_message': main_mess,
        'error message': error_mess
    }
    return JsonResponse(csv_json)


def find_para(input_r0, input_max_dur, input_mult):
    # search for matching model
    return Parameter.objects.filter(r0_value=input_r0,
                                    max_dur=input_max_dur,
                                    mult=input_mult)


def create_para(input_r0, input_max_dur, input_mult):
    p = Parameter(r0_value=input_r0,
                  max_dur=input_max_dur,
                  mult=input_mult).save()
    print('created new set')
    # save new parameter set without date updated
    p.save()
    print('saving new set')
    return p


def get_para(input_r0, input_max_dur, input_mult):
    with transaction.atomic():
        para_search = find_para(input_r0, input_max_dur, input_mult)
        if len(para_search) == 0:
            this_p = create_para(input_r0, input_max_dur, input_mult)
        else:
            this_p = para_search[0]
        return this_p


def update_model(this_p, input_r0, input_max_dur, input_mult):
    with transaction.atomic():
        # select for update locks these rows until the end of the transaction
        output_search = Output.objects.select_for_update().filter(
            paramID=this_p).order_by('_day_since_zero')
        has_output = len(output_search) != 0
        print('found' + str(len(output_search)) + 'output entries')
        # pass local model results to output objects
        new_model = Model_30_set(input_r0, input_max_dur, input_mult)
        for i in range(Model_30_get_size(new_model)):
            days_since = datetime.timedelta(days=i)
            this_date = this_p.day_zero + days_since
            # if there is prev output object, update
            if has_output and i <= len(
                    output_search
            ) - 1 and not output_search[i].was_updated_today():
                output_search[i]._new_cases = (Model_30_get_cases(
                    new_model, i))
                output_search[i]._date_updated = datetime.date.today()
            # otherwise create new output object
            else:
                o = Output(paramID=this_p,
                           _day=this_date,
                           _day_since_zero=i,
                           _new_cases=Model_30_get_cases(new_model, i),
                           _date_updated=datetime.date.today())
                o.save()
        # update date
        this_p.date_updated = datetime.date.today()
        this_p.time_updated = datetime.datetime.time.now()
        this_p.model_size = Model_30_get_size(new_model)
        print('date updated')
        this_p.save()
        print(this_p)


def days_to_csv(param_id):
    days = Output.objects.filter(paramID=param_id).order_by('_day_since_zero')
    output = "day,cases\n"
    for row in days:
        output += str(row._day_since_zero) + "," + str(row._new_cases) + "\n"
    return output


def get_output(this_p, input_r0, input_max_dur, input_mult):
    if this_p.was_updated_today():
        output = days_to_csv(this_p)
    else:
        update_model(this_p, input_r0, input_max_dur, input_mult)
        output = days_to_csv(this_p)
    return output
