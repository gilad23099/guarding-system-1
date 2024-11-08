import heapq
from datetime import datetime,timedelta
import copy

def main(guard_availability_day, guard_availability_night):
    # each shift is num_hours/len(guard_availability_day)
    # Example usage:
    guard_availability_day = [
    {0,4,5,6,8,9},  # gilad 
    {0,1,2,6,8,9},  # zvi 
    {0,1,4,5,6,7},  # nir 
    {0,1,2,3,4,5,6,7,8,9},  # gidon  
    {0,1,2,3,4,5,6,7,8,9},  # masad 
    {0,1,2,3},  # shachar 
    {0,1,2,3,4,5,6,7,8,9,13}, # morad 
    {0,7,8,9}, # kurzweil 
    {2,3}, #adi 
    {0,1,2,3,4,5,6,7,8,9}, #lior
    {3,4,6,8,9,10,11,12}, # elroei
    {5,6,7,8,9,10}, # drori
    {1,3,4,7,8,9,10,13}, # menashe
    {2,3,5,6,8,9,10} #funaro
]
    guard_availability_night = [
    {0,1,2,3,4,5,6,7,8,9,13},  # gilad 
    {0,1,2,3,4,5,6,7,8,9},  # zvi 
    {0,1,2,3,4,5,6,7,8,9,13},  # nir 
    {0,1,2,3,4,5,6,7,8,9,12},  # gidon  
    {0,1,2,3,4,5,6,7,8,9},  # masad 
    {0,1,2,3,4,5,6,7,8,9,11},  # shachar 
    {0,1,2,3,4,5,6,7,8,9}, # morad 
    {0,1,2,3,4,5,6,7,8,9,10,11}, # kurzweil 
    {0,1,2,3,4,5,6,7,8,9}, #adi 
    {0,1,2,3,4,5,6,7,8,9,11,12,13}, #lior 
    {3,4,6,8,9,10,11,12}, # elroei
    {5,6,7,8,9,10}, # drori
    {1,3,4,7,8,9,10,13}, # menashe
    {2,3,5,6,8,9,10} #funaro
]


    num_to_guards_dict={0:"gilad",1:"zvi",2:"nir",3:"gidon",4:"masad",5:"shachar",6:"morad",7:"kurzweil",8:"adi",9:"lior",10:"elroei",11:"drori",12:"menashe",13:"funaro"}
    guard_heap=[]


    ####################################################################
    # day set up
    ####################################################################

    num_hours=17 
    start_time_h=7
    start_time_m=0
    day_or_night="day"
    start_time,time_to_add=set_time(guard_availability_day,num_hours,day_or_night,start_time_h,start_time_m)

    # Call the function
    solution1 = greedy_guarding_schedule_day(guard_availability_day,guard_heap,0)
    # print the schedule
    print_schedule(solution1,day_or_night,num_to_guards_dict,time_to_add,num_hours,start_time,start_time_h,start_time_m)
    

    ####################################################################
    # night set up
    ####################################################################

    num_hours=7 
    start_time_h=0
    start_time_m=0
    day_or_night="night"
    start_time,time_to_add=set_time(guard_availability_night,num_hours,day_or_night,start_time_h,start_time_m)

    # Call the function
    if solution1 is not None:
        solution2= greedy_guarding_schedule_night(guard_availability_night,guard_heap,len(solution1))  
    else:
        solution2= greedy_guarding_schedule_night(guard_availability_night,guard_heap,0)

    # print the schedule
    print_schedule(solution2,day_or_night,num_to_guards_dict,time_to_add,num_hours,start_time,start_time_h,start_time_m)


    ####################################################################
    # day set up
    ####################################################################

    num_hours=5 
    start_time_h=7
    start_time_m=0
    day_or_night="day"
    start_time,time_to_add=set_time(guard_availability_day,num_hours,day_or_night,start_time_h,start_time_m)

    # Call the function
    if solution2 is not None:
        solution1 = greedy_guarding_schedule_day(guard_availability_day,guard_heap,len(solution1)+len(solution2))
    else:
        solution1 = greedy_guarding_schedule_day(guard_availability_day,guard_heap,0)    
    # print the schedule
    print_schedule(solution1,day_or_night,num_to_guards_dict,time_to_add,num_hours,start_time,start_time_h,start_time_m)
    print("total shifts per guard:")
    for item in guard_heap:
        total_hours,available_hours,last_location_in_solution,guard=item
        print(f"name: {num_to_guards_dict[guard]} , total: {total_hours}")

        
    return solution1,solution2    



######################################################################################
# scheduling day shifts when only 1 person guard at a time
######################################################################################
def greedy_guarding_schedule_day(guard_availability_day,guard_heap,num_of_guards_assigned): 
    """
    Modified greedy algorithm to assign guards to shifts while balancing distribution
    and prioritizing guards with fewer remaining available hours.
    
    Args:
    - guard_availability_day: A list of sets, where guard_availability_day[i] contains the hours that guard i can work.

    Returns:
    - A list of guard assignments, where each element represents the guard assigned to that hour.
    """
    num_guards = len(guard_availability_day)

    # Priority queue to keep track of guards by their current total assigned hours and remaining available hours
    #guard_heap = []
    
    # Initialize the heap with (total_hours_worked, remaining_available_hours, guard_id)
    if num_of_guards_assigned==0:
        for i in range(num_guards):
            available_hours = len(guard_availability_day[i])
            last_location_in_solution=-1
            heapq.heappush(guard_heap, (0, available_hours,last_location_in_solution,i))  # Initially, all guards have worked 0 hours

    else:
        t_heap=[]
        while guard_heap:
            total_hours, remaining_hours,last_location_in_solution,guard = heapq.heappop(guard_heap)
            remaining_hours=len(guard_availability_day[guard])
            heapq.heappush(t_heap,(total_hours, remaining_hours,last_location_in_solution,guard))
        while t_heap:
            curr_guard = heapq.heappop(t_heap)
            heapq.heappush(guard_heap,curr_guard)


        # Solution list where each index corresponds to the guard assigned for that hour
    solution = [-1] * num_guards
    
    # Assign each hour to the most suitable guard
    for hour in range(num_guards):
        assigned = False
        temp_heap = []  # Temporary heap to reinsert guards after checking availability
        guard_assigned="null"
        # Try to assign this hour to the most suitable guard
        while guard_heap:
            total_hours, remaining_hours,last_location_in_solution,guard = heapq.heappop(guard_heap)
            
            if hour in guard_availability_day[guard]:
                # If the guard can work this hour, assign them to it
                solution[hour] = guard
                total_hours += 1  # Increment the guard's worked hours
                remaining_hours -= 1  # Reduce the guard's available hours
                last_location_in_solution=hour + num_of_guards_assigned
                
                # Push the guard back into the heap with updated total hours and remaining available hours
                guard_assigned=(total_hours, remaining_hours,last_location_in_solution,guard)
                assigned = True
                break
            
            # If the guard is not available for this hour, add them to the temp heap
            temp_heap.append((total_hours, remaining_hours,last_location_in_solution,guard))
        
        # Reinsert guards back into the heap who couldn't be assigned this hour
        while guard_heap:
            total_hours, remaining_hours,last_location_in_solution,guard = heapq.heappop(guard_heap)
            if hour in guard_availability_day[guard]:
                remaining_hours-=1 # delete the current hour from the remaining hours set
            temp_heap.append((total_hours, remaining_hours,last_location_in_solution,guard))

        for item in temp_heap:
            heapq.heappush(guard_heap, item)
        if guard_assigned!="null":
            heapq.heappush(guard_heap, guard_assigned) 
        if not assigned:
            return None  # No valid assignment was possible for this hour (optional failure handling)
        
    # print("guard heap at the end of func day:")    
    # for item in guard_heap:
    #     print(item)
    return solution
######################################################################################
# scheduling night shifts when 2 persons guard at a time
######################################################################################
def greedy_guarding_schedule_night(guard_availability_night,guard_heap,num_of_guards_assigned):

    
    
    # reset the guard_heap with available_hours as at the begining of the day and leaving the rest the same
    night_heap=[]
    while guard_heap:
        if len(guard_heap)==1:
            break
        total_hours, remaining_hours,last_location_in_solution,guard = heapq.heappop(guard_heap)
        available_hours=len(guard_availability_night[guard])
        heapq.heappush(night_heap, (total_hours,available_hours,last_location_in_solution,guard))    
      
    

    num_guards=len(night_heap)
    solution = [[-1, -1] for _ in range(num_guards // 2)]
    


    #working now on the night_heap that contains all the guard except the guard that was last guarded
    for hour in range(num_guards//2):
        assigned=False
        temp_heap=[]
        guard_assigned1="null"
        guard_assigned2="null"
        # Try to assign this hour to the most suitable guard
        while night_heap:
            total_hours, remaining_hours,last_location_in_solution,guard = heapq.heappop(night_heap)
            
            if hour in guard_availability_night[guard]:
                # If the guard can work this hour, assign them to it
                 
                total_hours += 1  # Increment the guard's worked hours
                remaining_hours -= 1  # Reduce the guard's available hours
                last_location_in_solution = hour + num_of_guards_assigned # keeping as much rest time between shift of the same guard

                if solution[hour][0]==-1:
                    solution[hour][0] = guard
                    guard_assigned1=(total_hours, remaining_hours,last_location_in_solution,guard)   
                else:   
                    solution[hour][1]=guard 
                    guard_assigned2=(total_hours, remaining_hours,last_location_in_solution,guard)
                
                # Push the guard back into the heap with updated total hours and remaining available hours
                
                if solution[hour][0]!=-1 and solution[hour][1]!=-1: #succesfully assigned two guards to a shift
                    assigned = True
                    break
            
            # If the guard is not available for this hour, add them to the temp heap
            if solution[hour][0]==-1:
                temp_heap.append((total_hours, remaining_hours,last_location_in_solution,guard))
        
        # Reinsert guards back into the heap who couldn't be assigned this hour
        while night_heap:
            total_hours, remaining_hours,last_location_in_solution,guard = heapq.heappop(night_heap)
            if hour in guard_availability_night[guard]:
                remaining_hours-=1 # delete the current hour from the remaining hours set
            temp_heap.append((total_hours, remaining_hours,last_location_in_solution,guard))

        for item in temp_heap:
            heapq.heappush(night_heap, item)
        if guard_assigned1!="null" and guard_assigned2!="null":
            heapq.heappush(night_heap, guard_assigned1)    
            heapq.heappush(night_heap, guard_assigned2)    
        if not assigned:
            return None  # No valid assignment was possible for this hour (optional failure handling)
    

    guard_heap+=night_heap.copy() # guard heap remains without changes except available_hours that is set to the original set          
    heapq.heapify(guard_heap)
    

    return solution
######################################################################################
# the function returns start time of the shift and time of each shift
######################################################################################
def set_time(guard_availability,num_hours,day_or_night,start_time_h,start_time_m):
    if day_or_night=="day":
        time_of_each_shift=num_hours/len(guard_availability)
    else:
        time_of_each_shift=num_hours/((len(guard_availability)-1)//2)
    time_of_each_shift=round(time_of_each_shift,2)
    time_of_each_shift_h=int(time_of_each_shift)
    time_of_each_shift_m=str(time_of_each_shift).split(".")[1]
    time_of_each_shift_m=int(time_of_each_shift_m)
    if time_of_each_shift_m<10:
        time_of_each_shift_m=time_of_each_shift_m*10
    start_time=datetime(year=2024, month=10, day=13,hour=start_time_h,minute=start_time_m)
    time_to_add = timedelta(hours=time_of_each_shift_h, minutes=(time_of_each_shift_m*60//100))
    return (start_time,time_to_add)
######################################################################################
# the function prints the solution with all the shifts hours and guards assignments
######################################################################################
def print_schedule(solution,day_or_night,num_to_guards_dict,time_to_add,num_hours,start_time,start_time_h,start_time_m):
    if solution is not None:
        for i in range(len(solution)-1):
            # Format start_time and start_time + time_to_add to show only hours and minutes
            shift_start = start_time.strftime("%H:%M")
            shift_end = (start_time + time_to_add).strftime("%H:%M")
            if day_or_night=="day":
                solution[i] = f"{shift_start} - {shift_end} :: {num_to_guards_dict[solution[i]]}"
            else:
                solution[i] = f"{shift_start} - {shift_end} :: {num_to_guards_dict[solution[i][0]]},{num_to_guards_dict[solution[i][1]]}"
            start_time += time_to_add

        # Adjust the last shift to cover the remaining time

        final_shift_end = datetime(year=2024, month=10, day=13, hour=start_time_h, minute=start_time_m) + timedelta(hours=num_hours)
        shift_start = start_time.strftime("%H:%M")
        shift_end = final_shift_end.strftime("%H:%M")
        if day_or_night=="day":
            title="the guarding schedule for the day:"
            solution[-1] = f"{shift_start} - {shift_end} :: {num_to_guards_dict[solution[-1]]}"
        else:
            title="the guarding schedule for the night:"
            solution[-1] = f"{shift_start} - {shift_end} :: {num_to_guards_dict[solution[-1][0]]},{num_to_guards_dict[solution[-1][1]]}"
            

        # Print the resulting guard assignments
        print(title)
        print("-" * len(title))
        for assignment in solution:
            print(assignment)
    else:
        if day_or_night=="day":
            print("No valid guard assignment found for the day.")
        else:
            print("No valid guard assignment found for the night.")
########################################################################
if __name__ == '__main__':
    main()