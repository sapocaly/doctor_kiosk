(function () {
    var app = angular.module('myApp', []);
    app.config(function ($httpProvider) {
        //django csrf requirement
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
        //encode params in url
        $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
    });

    //convert seconds to proper time format
    app.filter('secondsToDateTime', [function () {
        return function (seconds) {
            return new Date(1970, 0, 1).setSeconds(seconds);
        };
    }]);

    app.controller('myCtrl', function ($scope, $timeout, $http) {
        // set appointment status to In Session and post to remote
        $scope.start_appointment = function (appointment) {
            appointment.status = 'In Session';
            // freeze the waited time in the scope
            appointment.time_waited = appointment.time_waited + $scope.time_counter;
            $scope.current = appointment;
            // remove appointment from apoointment list
            var index = $scope.appointments.indexOf(appointment);
            $scope.appointments.splice(index, 1);
            var url = "/api/appointment/";
            var params = {
                'id': appointment.id,
                'status': 'In Session'
            };
            api_post(url, params, function () {
                console.log('success update remote');
                // may want to sync data from server
            });

        };

        // set appointments properly and post to remote
        $scope.finish_appointment = function (appointment) {
            appointment.status = 'Complete';
            // put into appointment list again
            $scope.appointments.push(appointment);
            $scope.current = null;
            var url = "/api/appointment/";
            var params = {
                'id': appointment.id,
                'status': 'Complete'
            };
            api_post(url, params, function () {
                    console.log('success remote updated');
                    // refresh data so appointments remain ordered by time
                    $scope.refresh_data();
                }
            );
        };

        // refresh all the data
        $scope.refresh_data = function () {
            api_get("/api/appointment_list/", {}, function (response) {
                    $scope.appointments = response.data.data.appointments;
                    $scope.current = response.data.current;
                    // since all data are updated, reset the timer
                    $scope.time_counter = 0;
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

        // api get helper function
        function api_get(url, params, callback) {
            $http.get(url, {
                params: params
            })
                .then(callback)
                .catch(function (response) {
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
    });
})();