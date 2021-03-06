(function () {
    var app = angular.module("myApp", ['ngProgress', 'moment-picker', 'ngIdle', 'ui.bootstrap']);

    app.config(['$httpProvider',
        function ($httpProvider) {
            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
            $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
        }
    ]);

    app.config(function (IdleProvider) {
        IdleProvider.idle(5);
        IdleProvider.timeout(5);
    });

    app.controller('myCtrl', function ($scope, $http, ngProgressFactory, Idle, $uibModal) {
        $scope.step = 1;
        $scope.progressbar = ngProgressFactory.createInstance();
        $scope.states = states;

        // back to previous step
        $scope.prev = function () {
            $scope.step--;
        }

        function set_up_connection() {
            $scope.chatsock = new ReconnectingWebSocket('ws://' + window.location.host);
        };

        function send_message(message) {
            var message = {
                message: message,
            }
            $scope.chatsock.send(JSON.stringify(message));
        }

        // step one function, check patient info
        $scope.check_patient_info = function () {
            // make sure form filled
            if ($scope.first_name && $scope.last_name && $scope.email) {
                $scope.progressbar.start();
                api_get("/api/patient/",
                    {
                        "first_name": $scope.first_name,
                        "last_name": $scope.last_name,
                        "email": $scope.email,
                    },
                    function (response) {
                        $scope.progressbar.complete();
                        // assuming all f_name, l_name, email combination is unique
                        $scope.patient = response.data.data[0];
                        if ($scope.patient) {
                            // move to step two
                            $scope.step = 2;
                            $scope.get_appointment_info();
                            // no matching patient found
                        } else {
                            show_dialog(BootstrapDialog.TYPE_DANGER, 'No Matching Patient Found', 'Hello, stranger!')
                        }
                    });
            } else {
                show_dialog(BootstrapDialog.TYPE_DANGER, 'Not Enough Information', 'We need them all.')
                // to-do: highlight empty ones
            }
        };

        get_doctor = function () {
            api_get("/api/doctor/", {}, function (response) {
                $scope.doctor = response.data;
            });
        }

        $scope.get_appointment_info = function () {
            $scope.progressbar.start();
            $scope.error_2 = '......retrieving appointment information....';
            $scope.waiting_count = 0;
            $scope.appointment = null;

            api_get("/api/appointment_list/", {}, function (response) {
                $scope.progressbar.complete();
                var appointments = response.data.data.appointments;
                for (var j = 0; j < appointments.length; j++) {
                    app = appointments[j];
                    // only first confirmed appointment can be checked in, maybe support multiple check in in the future
                    if (!$scope.appointment && app.status == 'Confirmed' && app.patient.id == $scope.patient.id) {
                        $scope.appointment = app;
                    }
                    // meantime, count current waiting
                    if (app.status == 'Arrived') {
                        $scope.waiting_count++;
                    }
                }
                $scope.start();
                $scope.error_2 = null;
                if ($scope.appointment) {
                    // nothing really, the confirm button will show up automatically
                    null;
                } else {
                    show_dialog(BootstrapDialog.TYPE_WARNING, 'No Appointment Found', 'Have you confirmed your appointment with your doctor?')
                }
            });
        };

        // as its name suggests
        $scope.appointment_check_in = function () {
            $scope.progressbar.start();
            var params = {
                'id': $scope.appointment.id,
                'status': 'Arrived',
            };
            api_post("/api/appointment/", params, function (response) {
                $scope.progressbar.complete();
                // this is bad, should not happen
                if (!response.data.success) {
                    console.error(response.data.error);
                } else {
                    var average_min = parseInt($scope.doctor.lifetime_waiting / $scope.doctor.lifetime_appointment_count / 60);
                    // this is a long string
                    message = $scope.patient.first_name + ' ' + $scope.patient.last_name + ' arrived';
                    send_message(message);
                    show_dialog(BootstrapDialog.TYPE_SUCCESS, 'Almost there!', 'Doctor is notified! There are '
                        + $scope.waiting_count + ' people before you. Average waiting time is ' + average_min + ' minutes');
                    $scope.step = 3;
                }
            });
        };

        // push patient info to server, show dialog bas on success/fail
        $scope.update_patient_info = function () {
            $scope.progressbar.start();
            var params = {
                'id': $scope.patient.id,
                'email': $scope.patient.email,
                'address': $scope.patient.address,
                'social_security_number': $scope.patient.social_security_number,
                'zip_code': $scope.patient.zip_code,
                'cell_phone': $scope.patient.cell_phone,
                "date_of_birth": $scope.patient.date_of_birth,
                "city": $scope.patient.city,
                "state": $scope.patient.state,

            };
            //fields with blank input will not be updated at this time
            //to-do: fix the blank input, this might be handled easily from the backend
            api_post("/api/patient/", params, function (response) {
                $scope.progressbar.complete();
                if (!response.data.success) {
                    show_dialog(BootstrapDialog.TYPE_DANGER, "Don't panic", JSON.stringify(response.data.error));
                } else {
                    show_dialog(BootstrapDialog.TYPE_SUCCESS, 'Personal Info Updated', 'Thank you for your patience.', $scope.refresh_page);
                }
            });
        };


        function show_dialog(type, title, message, callback) {
            $scope.dialog = new BootstrapDialog({
                type: type,
                title: title,
                size: BootstrapDialog.SIZE_LARGE,
                message: message,
                onhidden: callback
            });
            $scope.dialog.open();
        }

        $scope.refresh_page = function () {
            location.reload();
        };

        // api helpers
        function api_get(url, params, callback) {
            $http.get(url, {
                params: params
            })
                .then(callback)
                .catch(function (response) {
                    console.error(response);
                });
        }

        function api_post(url, params, callback) {
            $http.post(url, $.param(params))
                .then(callback)
                .catch(function (response) {
                    console.error(response);
                });
        }

        // idle functions
        function closeModals() {
            if ($scope.dialog) {
                $scope.dialog.close();
            }
            if ($scope.warning) {
                $scope.warning.close();
                $scope.warning = null;
            }
        }

        $scope.$on('IdleStart', function () {
            closeModals();
            $scope.warning = $uibModal.open({
                templateUrl: 'warning-dialog.html',
                windowClass: 'modal-danger'
            });
        });

        $scope.$on('IdleEnd', function () {
            closeModals();
        });

        $scope.$on('IdleTimeout', function () {
            closeModals();
            $scope.refresh_page();
        });

        $scope.start = function () {
            Idle.watch();
        };

        get_doctor();
        set_up_connection();
    });
})();
