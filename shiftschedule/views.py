from django.shortcuts import render, redirect, get_object_or_404
from .models import Guard,Schedule,GuardShift
from .forms import GuardForm,TimeForm,UpdateGuardForm
from datetime import timedelta, datetime,date
from django.views.decorators.http import require_POST
from django.db.models import F
import heapq
import math

###############################################
# view functions for the html pages
###############################################

def index(request):
    return render(request, 'shiftschedule/index.html')

def add_guard(request):
    if request.method == "POST":
        form = GuardForm(request.POST)
        if form.is_valid():
            guard = form.save(commit=False)
            guard.available_shifts_day = guard.unavailable_hours_day
            guard.available_shifts_night = guard.unavailable_hours_night
            guard.save()
            return redirect('guards_list')  # Redirect to a success page or list page
    else:
        
        form = GuardForm()
    return render(request, 'shiftschedule/add_guard.html', {'form': form})

# update guard's unavailabilty in the day and night
def update_guard(request, guard_id):
    guard = get_object_or_404(Guard, id=guard_id)
    if request.method == 'POST':
        form = UpdateGuardForm(request.POST, instance=guard)
        if form.is_valid():
            guard = form.save(commit=False)
            guard.available_shifts_day = guard.unavailable_hours_day
            guard.available_shifts_night = guard.unavailable_hours_night
            form.save()  # This will save the updated fields to the database
            return redirect('guards_list')  # Redirect to a page after saving, e.g., a list of guards
    else:
        form = UpdateGuardForm(instance=guard)
    return render(request, 'shiftschedule/update_guard.html', {'form': form})


@require_POST
def delete_guard(request, guard_id):
    guard = get_object_or_404(Guard, id=guard_id)
    
    # Get the sequence number of the guard to be deleted
    deleted_sequence = guard.sequence_number
    
    # Delete the guard
    guard.delete()
    
    # Recalculate sequence numbers for all guards, starting from 1
    guards = Guard.objects.order_by('sequence_number')
    for i, g in enumerate(guards, start=0):
        if g.sequence_number != i:  # Only save if there's a change to avoid unnecessary saves
            g.sequence_number = i
            g.save()
    
    return redirect('guards_list')


def guards_view(request):
    guards = Guard.objects.all()
    context={
        'guards':guards
    }
    return render(request, 'shiftschedule/guards_list.html',context)


def reset_guard_time_func():

    guards=Guard.objects.all()
    for guard in guards:
        guard.available_shifts_day=guard.unavailable_hours_day
        guard.available_shifts_night=guard.unavailable_hours_night
        guard.save()


def time_view(request): #1
    if request.method == 'POST':
        form = TimeForm(request.POST)
        if form.is_valid():
            start_hour = form.cleaned_data['start_hour']  # Get the cleaned integer value
            start_minute = form.cleaned_data['start_minute']  # Get the cleaned integer value
            num_hours = form.cleaned_data['num_hours']  # Get the cleaned integer value
            shift = form.cleaned_data['shift']  # Get the cleaned integer value
            date = form.cleaned_data['date']  # Get the cleaned integer value
            context={
                'start_hour':start_hour,
                'start_minute':start_minute,
                'num_hours':num_hours,
                'shift':shift,
                'date':date,
            }
            reset_guard_time_func()
            set_guards_availabilty(start_hour,start_minute,num_hours,shift,date)
            return render(request,'shiftschedule/form_success.html',context)
    else:
        form = TimeForm()

    return render(request,'shiftschedule/time_form.html', {'form': form})  


def full_schedule(request):
    shifts = GuardShift.objects.select_related('guard', 'schedule').order_by('schedule__date', 'start_time', 'end_time')
    guards=Guard.objects.all()
    # Calculate total shifts for each guard
    total_shifts_per_guard = {}
    for shift in shifts:
        guard_name = shift.guard.name
        if guard_name in total_shifts_per_guard:
            total_shifts_per_guard[guard_name] += 1
        else:
            total_shifts_per_guard[guard_name] = 1

    # Build shifts list with total shifts included
    guards_shifts = [
        {
            'names': shift.guard.name,
            'start_time': shift.start_time,
            'end_time': shift.end_time,
            'date': shift.schedule.date,
            'total_shifts': total_shifts_per_guard[shift.guard.name]
        }
        for shift in shifts
    ]

    return render(request, 'shiftschedule/full_schedule.html', {'guards_shifts': guards_shifts,'guards':guards})


def reset_all_guard_fields(request):
    # Clear all field values in the Guard model
    guards=Guard.objects.all()
    for guard in guards:
        guard.available_shifts_day=guard.unavailable_hours_day
        guard.available_shifts_night=guard.unavailable_hours_night
        guard.last_location_in_solution=-1
        guard.total_hours_guarded=0
        guard.save()
    return redirect('index')  # Redirect to the index page or any other page



###############################################
#setting each guard his string of availabilty(day and night) -> gilad.available_shifts_day="0,1,2,3,4,5"
###############################################

def round_down(number, digits):
    factor = 10 ** digits
    return math.floor(number * factor) / factor


# handling the availabilty of guards when there is 
# at least one guard that can't guard at all at the current schedule 
def reset_field_empty_availabilty_case():
    guards=Guard.objects.all()
    for guard in guards:
        if guard.available_shifts_day != "":
            guard.available_shifts_day=guard.unavailable_hours_day
            guard.save()
    for guard in guards:
        if guard.available_shifts_night != "":
            guard.available_shifts_night=guard.unavailable_hours_night
            guard.save()    


def set_dict_of_shifts(start_hour,start_minute,num_hours,shift,date):
    # num_of_guards=Guard.objects.count() # 14 
    count_schedules=Schedule.objects.count()
    num_of_guards=Guard.objects.count() 
    guards=Guard.objects.all()
    # if count_schedules: # if there is more then one schedule handle the case that signed guards cant guard at the current schedule
    for guard in guards:
        if guard.available_shifts_day=="" and shift=="day":
            num_of_guards-=1    
        elif guard.available_shifts_night=="" and shift=="night":
            num_of_guards-=1
                
    start_minute_1=start_minute
    start_time=start_hour + start_minute/100  # 7 + 30/100 =7.3
    if shift=="day":
        shift_time = num_hours/num_of_guards # 17/14 = 1.214
        shift_time=round_down((shift_time-int(shift_time))*60/100 + int(shift_time),2) # (1.214 - 1)*60/100 = 0.1284 + 1 = 1.1284
        shift_time_minutes=round_down((shift_time-int(shift_time))*100,2) # ( 1.1284 -1 ) * 100 = 12.84
        dict_of_shifts={}
        for i in range(num_of_guards-1): # set the dictinoary of shifts { 0:(10.0-11.3),... }
            if start_minute+shift_time_minutes>=60:
                end_time=int(start_time)+int(shift_time)+ 1 # 7 + 1 + 1 = 9
                end_time+=round_down(((start_minute+shift_time_minutes)-60)/100,2) # (40 + 30 - 60) / 100 =0.1
                dict_of_shifts[i]=(round_down(start_time,2),round_down(end_time,2))
            else:
                end_time=start_time+shift_time
                dict_of_shifts[i]=(round_down(start_time,2),round_down(end_time,2))

            start_time=end_time
            start_minute=round_down((start_time-int(start_time))*100,2)     

        end_time=start_hour + start_minute_1/100 + num_hours    
        dict_of_shifts[num_of_guards-1]=(round_down(start_time,2),end_time)


    else:    
        shift_time=num_hours/(num_of_guards//2) # 17/14 = 1.214
        shift_time=round_down((shift_time-int(shift_time))*60/100 + int(shift_time),2) # (1.214 - 1)*60/100 = 0.1284 + 1 = 1.1284
        shift_time_minutes=round_down((shift_time-int(shift_time))*100,2) # ( 1.1284 -1 ) * 100 = 12.84
        dict_of_shifts={}
        for i in range(((num_of_guards)//2)-1): # set the dictinoary of shifts { 0:(10.0-11.3),... }
            if start_minute+shift_time_minutes>=60:
                end_time=int(start_time)+int(shift_time)+ 1 # 7 + 1 + 1 = 9
                end_time+=round_down(((start_minute+shift_time_minutes)-60)/100,2) # (40 + 30 - 60) / 100 =0.1
                dict_of_shifts[i]=(round_down(start_time,2),round_down(end_time,2))
            else:
                end_time=start_time+shift_time
                dict_of_shifts[i]=(round_down(start_time,2),round_down(end_time,2))

            start_time=end_time
            start_minute=round_down((start_time-int(start_time))*100,2) 

        end_time=start_hour + start_minute_1/100 + num_hours    
        dict_of_shifts[(num_of_guards)//2 -1]=(round_down(start_time,2),end_time)            

    return dict_of_shifts    


def guard_availability_to_dict(day_or_night): # "8-18,18-20" -> {gilad:(8,18),zvi:(18,20)}
    guards = Guard.objects.all()
    count=Guard.objects.count()
    dict_of_guards_availability = {}

    for guard in guards:
        guard_name = guard.name
        if day_or_night=="day" and guard.available_shifts_day=="":
            continue
        if day_or_night=="night" and guard.available_shifts_night=="":
            continue
        if guard_name not in dict_of_guards_availability:
            dict_of_guards_availability[guard_name] = []  # Initialize an empty list for this guard name

        # Split by comma if there are multiple ranges, or handle a single range without a comma
        if day_or_night=="day":
            if guard.available_shifts_day is None: #if the guard can guard at all the shifts
                continue    
            ranges = guard.available_shifts_day.split(',') if ',' in guard.available_shifts_day else [guard.available_shifts_day]
        else:
            if guard.available_shifts_night is None: #if the guard can guard at all the shifts
                continue
            ranges = guard.available_shifts_night.split(',') if ',' in guard.available_shifts_night else [guard.available_shifts_night]

        for range_pair in ranges:
            # Split by hyphen to separate start and end times
            start_time_restriction, end_time_restriction = range_pair.split('-')
            dict_of_guards_availability[guard_name].append((start_time_restriction, end_time_restriction))

    return dict_of_guards_availability

      
def set_guards_availabilty(start_hour, start_minute, num_hours, shift, date): #2
    guards = Guard.objects.all()
    count=Guard.objects.count()
    flag=False

    dict_of_shifts = set_dict_of_shifts(start_hour, start_minute, num_hours, shift, date)  # Example: {0: (7, 8.2), 1: (8.2, 9.4), ...}
    if shift=="day":
        dict_of_guards_availabilty = guard_availability_to_dict("day")  # Example: {"gilad": [(7, 8), (8, 9)], "zvi": [(10, 11), (12, 13)]}
    else:
        dict_of_guards_availabilty = guard_availability_to_dict("night")  # Example: {"gilad": [(7, 8), (8, 9)], "zvi": [(10, 11), (12, 13)]}    


    for guard, restricted_ranges in dict_of_guards_availabilty.items():
        result_string = ""

        # Convert restricted_ranges to float values for comparison
        restricted_ranges = [(float(start), float(end)) for start, end in restricted_ranges]

        # Loop through each shift in dict_of_shifts
        for shift_key, (shift_start, shift_end) in dict_of_shifts.items():
            # Check for overlap or containment  restricted 13:00(1)-15:00(2)  shift  11:48(1)-13:00(2)
            is_restricted = any(
                (restricted_start < shift_end and shift_start < restricted_end) for restricted_start, restricted_end in restricted_ranges
            )

            # If shift is not restricted, add the shift key to result string
            if not is_restricted:
                result_string += f"{shift_key},"

        result_string = result_string.rstrip(',')  # Remove trailing comma
        if result_string=="":
            flag=True
        # if result_string=='': # not counting the guards that cant guard at all
        #     count-=1

        # Update guard availability
        curr_guard = Guard.objects.get(name=guard)
        if shift == "day":
            curr_guard.available_shifts_day = result_string
        else:
            curr_guard.available_shifts_night = result_string
        curr_guard.save()  # Save the changes to the database

    result_string=''    
    for guard in guards: # handling the case that a guard has no restrictions -> not sure i have to write it
        if guard.available_shifts_day is None and shift=="day":
            for i in range(len(dict_of_guards_availabilty)):
                result_string+=f'{i},'
            result_string = result_string.rstrip(',')
            guard.available_shifts_day=result_string
            guard.save()
        if guard.available_shifts_night is None and shift=="night":
            for i in range((len(dict_of_guards_availabilty))//2):
                result_string+=f'{i},'
            result_string = result_string.rstrip(',')
            guard.available_shifts_night=result_string
            guard.save()

        result_string=''  

    if flag:
        reset_field_empty_availabilty_case()
        set_guards_availabilty(start_hour,start_minute,num_hours,shift,date)




###############################################
#algorithm for one guard at a shift and two guards at a shift returns: list of integers that represent guards.
###############################################

def build_heap_of_shifts(guard_availability,num_of_empty_guards,day_or_night):
    heap_of_shifts=[]
    count=0
    if day_or_night=="day":
        for i in range(len(guard_availability)-num_of_empty_guards):
            for availabilty_set in guard_availability:
                if i in availabilty_set:
                    count+=1
            heapq.heappush(heap_of_shifts, (count,i))  #(3-num of guards that can guard AT SHIFT NUMBER 0, 0-shift)
            count=0
    else:
        for i in range((len(guard_availability)-num_of_empty_guards)//2):
            for availabilty_set in guard_availability:
                if i in availabilty_set:
                    count+=1
            heapq.heappush(heap_of_shifts, (count,i))  #(3-num of guards that can guard AT SHIFT NUMBER 0, 0-shift)
            count=0        
    return heap_of_shifts  


def greedy_guarding_schedule_day(guard_availability_day,guard_heap,num_of_guards_assigned): 
    """
    Assigns guards to day shifts based on their availability using a greedy approach.
    This function pairs one guard for each day shift hour.

    Args:
        guard_availability_day (list of sets): Each set contains the day hours each guard is available.
        guard_heap (list): A min-heap used to prioritize guards based on a combination of four criteria:
            1. `total_hours`: Total hours the guard has already worked (guards with fewer hours are prioritized).
            2. `remaining_hours`: The number of remaining shifts the guard is available for (guards with more remaining shifts are prioritized).
            3. `last_location_in_solution`: The last shift the guard was assigned to (guards who haven’t worked recent shifts are prioritized).
            4. `guard_id`: A unique identifier for each guard (used as a tiebreaker if the previous criteria are equal).
        num_of_guards_assigned (int): The number of guards that can be assigned to shifts.

    Returns:
        list: A list of indices where each shift is being assigned by a guard.
        If a shift cannot be assigned, returns None.
    """

    # Initialize the number of guards and count of shifts already in the database
    num_guards = len(guard_availability_day)
    count=GuardShift.objects.count()
    num_of_empty_guards=0

    # Populate the guard_heap with guards based on initial total hours and availability,last location and id
    for i in range(num_guards):
        guard=Guard.objects.get(sequence_number=i)
        available_hours = len(guard_availability_day[i])

        # Count guards with no available hours for day shifts
        if not available_hours:
            num_of_empty_guards+=1
        last_location_in_solution=guard.last_location_in_solution
        total_hours=guard.total_hours_guarded

        # Push each guard into the heap based on total hours, availability,last location and id
        heapq.heappush(guard_heap, (total_hours, available_hours,last_location_in_solution,i))

    # Solution list where each index corresponds to the guard assigned for that hour
    solution = [-1] * (num_guards-num_of_empty_guards)

    # Build heap of shifts and their count in the guards availabilty set (e.g (3-count,0-shift))
    heap_of_shifts = build_heap_of_shifts(guard_availability_day,num_of_empty_guards,"day")
    # Main loop for assigning guards to each day shift hour
    while heap_of_shifts:
        _,hour=heapq.heappop(heap_of_shifts)
        assigned = False
        temp_heap = []  # Temporary heap to reinsert guards after checking availability
        guard_assigned="null"
        # Try to assign this hour to the most suitable guard
        while guard_heap:
            total_hours, remaining_hours,last_location_in_solution,id = heapq.heappop(guard_heap)
            guard=Guard.objects.get(sequence_number=id)

            # Check if the current guard is available at the hour
            if hour in guard_availability_day[id]:
                # Update guard's hours and last location
                solution[hour] = id
                total_hours += 1  # Increment the guard's worked hours
                remaining_hours -= 1  # Reduce the guard's available hours
                last_location_in_solution=hour+count
                guard.total_hours_guarded+=1
                guard.last_location_in_solution=last_location_in_solution
                guard.save()

                guard_assigned=(total_hours, remaining_hours,last_location_in_solution,id)
                assigned = True
                break
            
            # If the guard is not available for this hour, add them to the temp heap
            heapq.heappush(temp_heap,(total_hours, remaining_hours,last_location_in_solution,id))
        
        # Move remaining guards in guard_heap to temp_heap for further processing
        while guard_heap:
            curr_guard = heapq.heappop(guard_heap)
            heapq.heappush(temp_heap, curr_guard)     


        # for every guard, if he has the hour in the availabilty set, decrement he's reamainning hours by 1, because this hour was inserted with a guard now
        for item in temp_heap:
            total_hours, remaining_hours,last_location_in_solution,id=item
            if hour in guard_availability_day[id]:
                remaining_hours-=1 
            heapq.heappush(guard_heap,(total_hours, remaining_hours,last_location_in_solution,id))

        # Push the assigned guards back into the main heap with updated hours
        if guard_assigned!="null":
            heapq.heappush(guard_heap, guard_assigned) 

        # If no valid assignment for this hour, return None (optional failure handling)
        if not assigned:
            return None

    return solution


def greedy_guarding_schedule_night(guard_availability_night,guard_heap,num_of_guards_assigned):
    """
    Assigns guards to night shifts based on their availability using a greedy approach.
    This function pairs two guards for each night shift hour, prioritizing guards who have worked fewer hours.

    Args:
        guard_availability_night (list of sets): Each set contains the night hours each guard is available.
        guard_heap (list): A min-heap used to prioritize guards based on a combination of four criteria:
            1. `total_hours`: Total hours the guard has already worked (guards with fewer hours are prioritized).
            2. `remaining_hours`: The number of remaining shifts the guard is available for (guards with more remaining shifts are prioritized).
            3. `last_location_in_solution`: The last shift the guard was assigned to (guards who haven’t worked recent shifts are prioritized).
            4. `guard_id`: A unique identifier for each guard (used as a tiebreaker if the previous criteria are equal).
        num_of_guards_assigned (int): The number of guards that can be assigned to shifts.

    Returns:
        list of lists: A nested list where each inner list contains the indices of two assigned guards for each shift.
                       If a shift cannot be assigned, returns None.
    """
    # Initialize the number of guards and count of shifts already in the database
    num_guards = len(guard_availability_night)
    count=GuardShift.objects.count()
    num_of_empty_guards=0
    for i in range(num_guards):
        guard=Guard.objects.get(sequence_number=i)
        available_hours = len(guard_availability_night[i])
        if not available_hours:
            num_of_empty_guards+=1
        last_location_in_solution=guard.last_location_in_solution
        total_hours=guard.total_hours_guarded
        heapq.heappush(guard_heap, (total_hours, available_hours,last_location_in_solution,i))  # Initially, all guards have worked 0 hours

    # Solution list where each index corresponds to the guard assigned for that hour
    solution = [[-1, -1] for _ in range((num_guards-num_of_empty_guards) // 2)]


    # Build heap of shifts and their count in the guards availabilty set (e.g (3-count,0-shift))
    heap_of_shifts = build_heap_of_shifts(guard_availability_night,num_of_empty_guards,"night")
    while heap_of_shifts:
        _,hour=heapq.heappop(heap_of_shifts)
        assigned=False
        temp_heap=[]
        guard_assigned1=None
        guard_assigned2=None
        # Try to assign this hour to the most suitable guard
        while guard_heap:
            total_hours, remaining_hours,last_location_in_solution,id = heapq.heappop(guard_heap)
            guard=Guard.objects.get(sequence_number=id)
            # Check if the current guard is available at the hour
            if hour in guard_availability_night[id]:
               # Update guard's hours and last location
                total_hours += 1  # Increment the guard's worked hours
                remaining_hours -= 1  # Reduce the guard's available hours
                last_location_in_solution=hour+count
                guard.total_hours_guarded+=1
                guard.last_location_in_solution=last_location_in_solution
                guard.save()

                # Assign guard to the hour in the solution list
                if solution[hour][0]==-1:
                    solution[hour][0] = id
                    guard_assigned1=(total_hours, remaining_hours,last_location_in_solution,id)   
                else:   
                    solution[hour][1]=id
                    guard_assigned2=(total_hours, remaining_hours,last_location_in_solution,id)
                
                # Check if two guards have been assigned to this shift
                if solution[hour][0]!=-1 and solution[hour][1]!=-1: 
                    assigned = True
                    break
            else:
                # Add guards not assigned to the current hour to a temporary heap
                heapq.heappush(temp_heap,(total_hours, remaining_hours,last_location_in_solution,id))

        
        # Move remaining guards in guard_heap to temp_heap for further processing
        while guard_heap:
            curr_guard = heapq.heappop(guard_heap)
            heapq.heappush(temp_heap, curr_guard)

        #for every guard, if he has the hour in his availability set, decrement his remaining hours by 1, because this hour was inserted with a guard now    
        for item in temp_heap:
            total_hours, remaining_hours,last_location_in_solution,id=item
            if hour in guard_availability_night[id]:
                remaining_hours-=1 
            heapq.heappush(guard_heap,(total_hours, remaining_hours,last_location_in_solution,id))
        if guard_assigned1 is not None and guard_assigned2 is not None:
            heapq.heappush(guard_heap, guard_assigned1)    
            heapq.heappush(guard_heap, guard_assigned2)  
        else:
            # If no valid assignment for this hour, return None (optional failure handling)
            return None
    #     if not assigned:
    #         return None  # No valid assignment was possible for this hour (optional failure handling)
    return solution



###############################################
# main function and auxiliary functions
###############################################

def make_num_to_guard_dict():

    guards=Guard.objects.all()
    index=0
    sol_num_to_guard_dict={}
    for guard in guards:
        sol_num_to_guard_dict[index]=guard.name
        index+=1
    return sol_num_to_guard_dict   

def make_list_of_sets(day_or_night):
    guards = Guard.objects.all()
    if day_or_night=="day":
        lst_of_set_day=[]
        for guard in guards:
            if guard.available_shifts_day!="":
                lst_of_set_day.append(set(map(int, guard.available_shifts_day.split(','))))
            else:
                # If available_shifts_day is empty, add an empty set
                lst_of_set_day.append(set())    
        return lst_of_set_day
    else:
        lst_of_set_night=[]
        for guard in guards:
            if guard.available_shifts_night!="":
                lst_of_set_night.append(set(map(int, guard.available_shifts_night.split(','))))
            else:
                # If available_shifts_day is empty, add an empty set
                lst_of_set_night.append(set())    
        return lst_of_set_night
    
def check_empty_sets(guard_availability):# to handle cases where some guards cant guard at all
    number_of_not_empty_sets = len([single_set for single_set in guard_availability if single_set])
    return number_of_not_empty_sets

def set_time(guard_availability, num_hours, day_or_night, start_time_h, start_time_m):
    """
    Calculate the shift duration for each guard and determine the start and end times for shifts.

    Args:
        guard_availability (list of sets): List of sets containing the available hours for each guard.
        num_hours (float): Total number of hours for the shift.
        day_or_night (str): A string indicating whether the shift is 'day' or 'night'.
        start_time_h (int): The starting hour of the shift.
        start_time_m (int): The starting minute of the shift.

    Returns:
        tuple: The start time (datetime object) and the time to add (timedelta object) for each shift.
    """
    # Determine the time each shift will cover based on the total number of hours
    if day_or_night == "day":
        time_of_each_shift = num_hours / check_empty_sets(guard_availability)
    else:
        time_of_each_shift = num_hours / (check_empty_sets(guard_availability) // 2)
    
    # Round the time to 2 decimal places for more accurate time calculations
    time_of_each_shift = round(time_of_each_shift, 2)

    # Extract the hours and minutes from the decimal time
    time_of_each_shift_h = int(time_of_each_shift)
    time_of_each_shift_m = str(time_of_each_shift).split(".")[1]
    time_of_each_shift_m = int(time_of_each_shift_m)
    
    # Ensure that minutes are formatted correctly (e.g., 5 minutes should be 05)
    if time_of_each_shift_m < 10:
        time_of_each_shift_m = time_of_each_shift_m * 10
    
    # Create a start time using the provided hour and minute
    start_time = datetime(year=2024, month=10, day=13, hour=start_time_h, minute=start_time_m)
    
    # Calculate the time to add for each shift, based on the calculated shift duration
    time_to_add = timedelta(hours=time_of_each_shift_h, minutes=(time_of_each_shift_m * 60 // 100))

    return (start_time, time_to_add)


def list_to_full_schedule(solution, shift, num_to_guards_dict, time_to_add, num_hours, start_time, start_time_h, start_time_m):
    """
    Convert the solution to a full schedule format with proper start and end times for each guard.

    Args:
        solution (list): List containing the guard assignments (indices or names).
        shift (str): The type of shift ('day' or 'night').
        num_to_guards_dict (dict): A dictionary mapping guard indices to guard names.
        time_to_add (timedelta): The time interval between shifts.
        num_hours (float): The total number of hours for the shift.
        start_time (datetime): The start time for the first shift.
        start_time_h (int): The starting hour of the shift.
        start_time_m (int): The starting minute of the shift.

    Returns:
        list: A list of formatted strings representing the full schedule with shifts and guard assignments.
    """
    # Check if the solution is valid (non-None) before proceeding
    if solution is not None:
        for i in range(len(solution) - 1):
            # Format the start time and end time of each shift
            shift_start = start_time.strftime("%H:%M")
            shift_end = (start_time + time_to_add).strftime("%H:%M")

            # Format the schedule for day or night shifts differently
            if shift == "day":
                solution[i] = f"{shift_start} - {shift_end} :: {num_to_guards_dict[solution[i]]}"
            else:
                solution[i] = f"{shift_start} - {shift_end} :: {num_to_guards_dict[solution[i][0]]},{num_to_guards_dict[solution[i][1]]}"
            
            # Update the start time for the next shift
            start_time += time_to_add

        # Adjust the last shift to cover the remaining time
        final_shift_end = datetime(year=2024, month=10, day=13, hour=start_time_h, minute=start_time_m) + timedelta(hours=num_hours)
        shift_start = start_time.strftime("%H:%M")
        shift_end = final_shift_end.strftime("%H:%M")

        # Format the final shift for day or night
        if shift == "day":
            solution[-1] = f"{shift_start} - {shift_end} :: {num_to_guards_dict[solution[-1]]}"
        else:
            solution[-1] = f"{shift_start} - {shift_end} :: {num_to_guards_dict[solution[-1][0]]},{num_to_guards_dict[solution[-1][1]]}"

        return solution
    else:
        return None


def make_schedule(request):
    """
    Handles the scheduling of guards based on user input from a POST request.

    Args:
        request (HttpRequest): The incoming HTTP request containing form data.

    Returns:
        HttpResponse: Renders the schedule page with the generated guard schedule.
    """
    if request.method == 'POST':
        # Extract form data (start time, number of hours, shift type, date)
        start_hour = int(request.POST.get('start_hour')) 
        start_minute = int(request.POST.get('start_minute')) 
        num_hours = float(request.POST.get('num_hours'))
        num_hours = (num_hours - int(num_hours)) * 100 / 60 + int(num_hours)  # Convert to decimal time
        shift = request.POST.get('shift')
        date = request.POST.get('date')

        # Create a dictionary of guard names and their corresponding indices
        num_to_guards_dict = make_num_to_guard_dict()
        
        # Initialize guard heap for scheduling
        guard_heap = []  

        # Depending on the shift type, generate the corresponding availability list and solution
        if shift == "day":
            guard_availability_day = make_list_of_sets("day")
            solution1 = greedy_guarding_schedule_day(guard_availability_day, guard_heap, 0)
            start_time, time_to_add = set_time(guard_availability_day, num_hours, shift, start_hour, start_minute)
        else:
            guard_availability_night = make_list_of_sets("night")
            solution1 = greedy_guarding_schedule_night(guard_availability_night, guard_heap, 0)
            start_time, time_to_add = set_time(guard_availability_night, num_hours, shift, start_hour, start_minute)

        # Generate the full schedule with formatted start and end times
        solution1 = list_to_full_schedule(solution1, shift, num_to_guards_dict, time_to_add, num_hours, start_time, start_hour, start_minute)

        # Create a new schedule entry in the database
        new_schedule = Schedule.objects.create(
            date=date,  
            shift_type=shift
        )

        # Save each guard's shift to the GuardShift model
        if shift == "day":
            for i, guard_info in enumerate(solution1):
                guard_name = guard_info.split("::")[1].strip()
                start_time_str, end_time_str = guard_info.split("::")[0].strip().split(" - ")

                start_time_obj = datetime.strptime(start_time_str, "%H:%M").time()
                end_time_obj = datetime.strptime(end_time_str, "%H:%M").time()

                guard = Guard.objects.get(name=guard_name)

                GuardShift.objects.create(
                    guard=guard,
                    schedule=new_schedule,
                    start_time=start_time_obj,
                    end_time=end_time_obj
                )
        else:
            for i, guard_info in enumerate(solution1):
                guard_name_1 = guard_info.split("::")[1].split(",")[0].strip()
                guard_name_2 = guard_info.split("::")[1].split(",")[1].strip()
                start_time_str, end_time_str = guard_info.split("::")[0].strip().split(" - ")

                start_time_obj = datetime.strptime(start_time_str, "%H:%M").time()
                end_time_obj = datetime.strptime(end_time_str, "%H:%M").time()

                guard1 = Guard.objects.get(name=guard_name_1)
                guard2 = Guard.objects.get(name=guard_name_2)

                GuardShift.objects.create(
                    guard=guard1,
                    schedule=new_schedule,
                    start_time=start_time_obj,
                    end_time=end_time_obj
                )
                GuardShift.objects.create(
                    guard=guard2,
                    schedule=new_schedule,
                    start_time=start_time_obj,
                    end_time=end_time_obj
                )

        context = {'solution1': solution1}
        return render(request, 'shiftschedule/schedule.html', context)

    return redirect('index')







