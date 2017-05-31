(function () {
    var app = angular.module('myApp', ['ngProgress', 'ngToast']);
    app.config(function ($httpProvider) {
        //django csrf requirement
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
        //encode params in url
        $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
    });
    app.config(['ngToastProvider',
        function (ngToast) {
            ngToast.configure({
                horizontalPosition: 'right',
                maxNumber: 5
            })
        }
    ]);

    //convert seconds to proper time format
    app.filter('secondsToDateTime', [function () {
        return function (seconds) {
            return new Date(1970, 0, 1).setSeconds(seconds);
        };
    }]);

    app.controller('myCtrl', function ($scope, $timeout, $http, ngProgressFactory, ngToast) {
        $scope.progressbar = ngProgressFactory.createInstance();

        $scope.set_up_connection = function () {
            $scope.chatsock = new ReconnectingWebSocket('ws://' + window.location.host + "/doctor");
            $scope.chatsock.onmessage = function (message) {
                ngToast.create({
                    content: '<h2>' + message.data + '</h2>',
                });
                $scope.refresh_data();
            };
        };


        // set appointment status to In Session and post to remote
        $scope.start_appointment = function (appointment) {
            $scope.progressbar.start();
            appointment.status = 'In Session';
            // freeze the waited time in the scope
            //appointment.time_waited = appointment.time_waited + $scope.time_counter;
            $scope.current = appointment;
            // remove appointment from apoointment list
            var index = $scope.appointments.indexOf(appointment);
            $scope.appointments.splice(index, 1);
            var params = {
                'id': appointment.id,
                'status': 'In Session'
            };
            api_post("/api/appointment/", params, function () {
                console.log('success update remote');
                // may want to sync data from server
                $scope.refresh_data();
            });

        };

        // set appointments properly and post to remote
        $scope.finish_appointment = function (appointment) {
            $scope.progressbar.start();
            appointment.status = 'Complete';
            // put into appointment list again
            $scope.appointments.push(appointment);
            $scope.current = null;
            var params = {
                'id': appointment.id,
                'status': 'Complete'
            };
            api_post("/api/appointment/", params, function () {
                    console.log('success remote updated');
                    // refresh data so appointments remain ordered by time
                    $scope.refresh_data();
                }
            );
        };

        // refresh all the data
        $scope.refresh_data = function () {
            $scope.progressbar.start();
            api_get("/api/appointment_list/", {}, function (response) {
                    $scope.appointments = response.data.data.appointments;
                    $scope.current = response.data.data.current;
                    // since all data are updated, reset the timer
                    $scope.time_counter = 0;
                    $scope.progressbar.complete();
                }
            );
            $scope.get_doctor();
        };


        // automatically increment timer
        $scope.onTimeout = function () {
            $scope.time_counter++;
            $timeout($scope.onTimeout, 1000);
        };

        // get doctor info
        $scope.get_doctor = function () {
            api_get("/api/doctor/", {}, function (response) {
                $scope.my_doctor = response.data;
                $scope.avg_time = parseInt($scope.my_doctor.lifetime_waiting / $scope.my_doctor.lifetime_appointment_count / 60)
            });
        }

        // load data
        $scope.refresh_data();
        $timeout($scope.onTimeout, 1000);
        $scope.set_up_connection();

        // api get helper function
        function api_get(url, params, callback) {
            $http.get(url, {
                params: params
            })
                .then(callback)
                .catch(function (response) {
                    console.error(url);
                    console.error(params);
                    console.error(response);
                });
        }

        // api post helper function
        function api_post(url, params, callback) {
            $http.post(url, $.param(params))
                .then(callback)
                .catch(function (response) {
                    console.error(response);
                });
        }

        $scope.no_show_appointment = function (appointment) {
            $scope.progressbar.start();
            appointment.status = 'No Show';
            // put into appointment list again
            var params = {
                'id': appointment.id,
                'status': 'No Show'
            };
            api_post("/api/appointment/", params, function () {
                    console.log('success remote updated');
                    // refresh data so appointments remain ordered by time
                    $scope.refresh_data();
                }
            );
        };

        $scope.is_late = function (appointment) {
            return Date.parse(appointment.scheduled_time) < new Date();
        };
    });
})();