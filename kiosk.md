# functionalities
- dashboard
	- display appointment information
	- display waiting time for each appointment and the average
	- mark late appointment as no show
	- start arrived appointment
	- finish current session
	- patient arrival notification

- kiosk
	- retrieve patient infomation with name and email
	- retrieve patient's confirmed appointment
	- update patient's information
	- notify doctor
	- show current number in queue and average waiting time

	
# backend

- model
	- Doctor
		- __doctor_id__ 
		- first_name
		- last_name
		- access_token
		- lifetime\_waiting_time
		- lifetime\_appointment_count
	- AppointmentProfile
		- doctor
		- appointment_id
		- arrival_time
		- started_time
		- complete_time 


- view
	- index
	- kiosk
	- dashboard 

- websocket
	- connect
	- recv
	- disconnect

- api
	- patient(GET/POST)
	- appointment(POST)
	- appointment_list(GET)
	- doctor(GET) 

# issues & thoughts

- allow multiple current appointments in session?
- allow patient check in multiple appointments
- form validation for cell# and ssn
- update all data at real time with django channels
- form blank input update issue
