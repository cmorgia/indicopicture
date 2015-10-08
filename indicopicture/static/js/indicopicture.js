function movePictureBox(strategy) {
    var parent;
    if (strategy==undefined) {
        parent = $('.picturebox:first').parents('div.i-box-content');
    } else if (strategy==0) {
        parent = $('.picturebox:first').parents('table:first').parents('tr:first');
    } else if (strategy==1) {
        parent = $('.picturebox:first').parents('table:first').parents('tr:first');
    } else {
        console.log("Unexpected strategy for displaing picture: "+strategy);
    }

    $('.picturebox').appendTo(parent);
    //$('.picturebox').css({"position": "absolute", "top":"100px", "right":"250px","width":"225px"});
}

ndServices.provider('curl', function() {
    var baseUrl = Indico.Urls.Base;
    var modulePath = '';

    return {
        setModulePath: function(path) {
            if (path.substr(-1) == '/') {
                path = path.substr(0, path.length - 1);
            }

            modulePath = path;
        },

        $get: function() {
            return {
                tpl: function(path) {
                    return baseUrl + modulePath + '/tpls/' + path;
                }
            };
        }
    };
});

ndRegForm.config(function(curlProvider) {
    curlProvider.setModulePath('/static/assets/plugins/indicopicture');
});

ndRegForm.directive('ndPictureField', function(curl) {
    return {
        require: 'ndField',
        controller: function($scope) {
            $scope.tplInput = curl.tpl('picture.tpl.html');
        },

        link: function(scope,element) {
            scope.settings.fieldName = $T("Picture");
            scope.removeAttachment = function() {
                delete scope.userdata[scope.getName(scope.field.input)];
            };
            movePictureBox();
        }
    };
});

ndRegForm.value('Frozen',{frozen:false});

ndRegForm.controller('WebcamCtrl',function($scope,Frozen) {
    $scope.take_snapshot = function() {
        // take snapshot and get image data
        Webcam.snap(function (data_uri) {
            $('#picture_uri').val(data_uri);
        });
        $('.qtip:visible').qtip("hide");
    };

    $scope.toggle_freeze = function() {
        if (Frozen.frozen) {
            Webcam.unfreeze();
            $('#freeze').text("Freeze");
            Frozen.frozen = false;
        } else {
            Webcam.freeze();
            $('#freeze').text("Unfreeze");
            Frozen.frozen = true;
        }
    };
});

ndRegForm.directive('ndWebcam', function ($http, $compile, $templateCache, curl) {
    return {
        controller: 'WebcamCtrl',
        link: function (scope, element) {
            $http.get(curl.tpl('webcam.tpl.html'), {cache: $templateCache})
                .success(function (template) {

                    var content = $compile(template)(scope);

                    element.qtip({
                        content: {
                            title: {
                                text: $T('Take picture')
                            },
                            text: content
                        },

                        position: {
                            my: 'top center',
                            at: 'bottom center'
                        },

                        show: {
                            event: 'click',
                            solo: true,
                            modal: {
                                on: true
                            }
                        },

                        hide: false,

                        style: {
                            classes: 'regform-add-field-qtip',
                            name: 'light'
                        },

                        events: {
                            hide: function (event, api) {
                                Webcam.reset();
                            },
                            show: function (event, api) {
                                Webcam.set({width: 280, height: 210, image_format: 'jpeg', jpeg_quality: 90});
                                Webcam.attach('#my_camera');
                                var frozen = false;
                            }
                        }
                    });
                });
        }
    };
});
