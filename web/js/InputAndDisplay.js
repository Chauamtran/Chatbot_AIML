var app = angular.module("chatApp", []);
            app.factory('myMessage', function($http, $q, $log) {
                return{
                    getMessage: function(message){
                       var header = {
                            headers: {
                                'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8;'
                            }
                        }
                        var defer = $q.defer();
                        var timeOut;
                        timeOut = setTimeout(function() {
                            $http.get('http://chatbot.local/chatbot/action?message='+ message, header)
                                .success(function(data) {
                                    defer.resolve(data);
                                })
                                .error(function(msg, code) {
                                    defer.reject(msg);
                                    $log.error(msg, code);
                                });
                            clearTimeout(timeOut);
                        }, 100);
                        return defer.promise;
                  },
                }
            })

            app.controller('chatCtrl', function($scope, $http, myMessage){
                $(document).ready(function(){
                    $("#showMessage").append('<div><b>Bot</b>: Hello! What can I do for you?</div>')

                    $("#usermsg").keypress(function (e) {
                        if(e.which == 13) {
                            var inputUserMessage = document.getElementById("usermsg").value;
                            if (inputUserMessage.value != '') {
                                $("#showMessage").append('<div><b>Human</b>: ' + inputUserMessage + '</div>')
                            }
                            e.preventDefault();
                            $scope.postMessageFunc(e);
                            $("#usermsg").val('');
                        }
                    });
                });

                $scope.postMessageFunc = function(e){
                    var userM = document.getElementById("usermsg").value;
                    myMessage.getMessage(userM).then(function successCallback(data) {
                        $("#showMessage").append('<div><b>Bot</b>: ' + data['message'] + '</div>')
                    })

                }
            })