// system1
var sendingData = { unwantImages: [], importantImages: [], number: 0, projectName: '' };

browseFolder = () => {
    eel.browse("system1_folder")(r => {
        if (r != 'path_error!') {
            $('#optionPanel>img').remove();
            drawOptionTrees(r);
            $('#browseBtn').prop('disabled', false).html('Open...');
        } else {
            $('#browseBtn').prop('disabled', false).html('Open...');
            console.error(r);
        }
    });
    $('#browseBtn').prop('disabled', true).html(`<span class="spinner-grow spinner-grow-sm"></span>Opening..`);
}

drawOptionTrees = (r = []) => {
    let data = JSON.parse(r);

    $('#resourceTree').jstree('destroy');
    $('#resourceTree')
        .on('changed.jstree', (e, d) => {
            $('#previewRes').removeClass('invisible');
            let checked = $('#resourceTree').jstree('is_checked', d.node);
            if (checked === true) {
                let path = d.node.original.path;
                if (path)
                    getImgSrc(path).then(r => {
                        $('#previewRes').prop('src', 'data:image/png;base64,' + r);
                    });
            }
            else {
                $('#previewRes').prop('src', "./assets/images/null.jpg");
            }
        })
        .jstree({
            "plugins": ["wholerow", "checkbox"],
            "core": {
                "data": data,
            }
        });

    $('#resourceTree2')
        .on('changed.jstree', (e, d) => {
            $('#previewRes2').removeClass('invisible');

            let checked = $('#resourceTree2').jstree('is_checked', d.node);

            if (checked === true) {
                let path = d.node.original.path;
                let thisItemParent = d.node.parent;
                let thisID = d.node.id;
                let checkedItems = $('#resourceTree2').jstree('get_checked');

                checkedItems.forEach((arg) => {
                    argParent = $('#resourceTree2').jstree('get_node', arg).parent;
                    if (thisItemParent == argParent && thisID != arg) {
                        $('#resourceTree2').jstree('uncheck_node', arg);
                    }
                });
                if (path)
                    getImgSrc(path).then(r => {
                        $('#previewRes2').prop('src', 'data:image/png;base64,' + r);
                    });

            }
            else {
                $('#previewRes2').prop('src', "./assets/images/null.jpg");
            }
        })
        .jstree({
            "plugins": ["wholerow", "checkbox", "search"],
            "core": {
                "data": data,
                // "multiple": false
            },
            "checkbox": {
                three_state: false,
                cascade: "none"
            }
        });
}

getImgSrc = async function (path) {
    let result = await eel.getImgSrc(path)();
    return result;
}

getUnwantedItems = () => {
    sendingData.unwantImages = [];
    var temp1 = $('#resourceTree').jstree('get_checked', () => { });
    var array = temp1,
        result = array.reduce((r, { parent: group, ...object }) => {
            var temp = r.find(o => o.group === group);
            if (!temp) r.push(temp = { group, children: [] });
            temp.children.push(object);
            return r;
        }, []);

    return result;
}

getImportantItems = () => {
    sendingData.importantImages = [];
    var temp1 = $('#resourceTree2').jstree('get_checked', () => { });
    var array = temp1,
        result = array.reduce((r, { parent: group, ...object }) => {
            var temp = r.find(o => o.group === group);
            if (!temp) r.push(temp = { group, children: [] });
            temp.children.push(object);
            return r;
        }, []);
    return result;
}


$('#generate').on('click', () => {

    let checkedItems = $('#resourceTree').jstree('get_checked');
    if (checkedItems.length === 0) {
        alert('Please select resourceTree at least one node.');
        return;
    }
    if ($('#projectName').val() === '') {
        alert('Please input your project name.');
        return;
    }
    if ($('#uploadURL').val() === '') {
        alert('Please input URL for uploading:');
        return;
    }

    $('#generate').prop('disabled', true);
    $('#optionPanel4 .progress-bar').addClass('progress-bar-animated');
    $('#reset').prop('disabled', true);
    sendingData.unwantImages = getUnwantedItems();
    sendingData.importantImages = getImportantItems();
    sendingData.number = $('#repeatNum').val();
    sendingData.projectName = $('#projectName').val();
    sendingData.uploadURL = $('#uploadURL').val();

    eel.combineImages(JSON.stringify(sendingData))(r => {
        if (r == 'success') {
            $('#optionPanel4 .progress-bar').removeClass('progress-bar-animated');
            $('#reset').prop('disabled', false);
            $('#generate').prop('disabled', false);
        }
    });
});

$('#reset').on('click', () => {
    document.location.reload();
});

// system2
browseExcel = () => {
    eel.browse('system2_excel')(r => {
        if (r != 'path_error!') {
            $('#browseBtn2').prop('disabled', false).html('Open...');
        } else {
            $('#browseBtn2').prop('disabled', false).html('Open...');
            console.error(r);
        }
    });
    $('#browseBtn2').prop('disabled', true).html(`<span class="spinner-grow spinner-grow-sm"></span>Opening..`);
}

browseBg = () => {
    eel.browse('system2_bg')(r => {
        if (r != 'path_error!') {
            $('#browseBtn3').prop('disabled', false).html('Open...');
        } else {
            $('#browseBtn3').prop('disabled', false).html('Open...');
            console.error(r);
        }
    });
    $('#browseBtn3').prop('disabled', true).html(`<span class="spinner-grow spinner-grow-sm"></span>Opening..`);
}


$('#generate2').on('click', () => {
    $('#generate2').prop('disabled', true);
    $('#optionPanel6 .progress-bar').addClass('progress-bar-animated');
    $('#reset2').prop('disabled', true);
    eel.combineImages2($('#repeatNum2').val())(r => {
        if (r == 'success') {
            $('#optionPanel6 .progress-bar').removeClass('progress-bar-animated');
            $('#reset2').prop('disabled', false);
            $('#generate2').prop('disabled', false);
        }
    });
});

$('#reset2').on('click', () => {
    document.location.reload();
});


// system3
$(document).ready(() => {

    $('input[name="modeSwitch"]').change((e) => {
        let val = e.target.defaultValue;
        let autoOptions = `<div class="col-4"></div><div class="col-4">
                                <div class="card">
                                    <div class="card-header ">
                                    Set the number of iterations of the fractal algorithm<br>(If the number of iterations is too large, your device may be stopped.)
                                    </div>
                                    <div class="card-body">
                                        <div class="input-group mb-3">
                                            <div class="input-group-prepend">
                                                <span class="input-group-text">Iterations</span>
                                            </div>
                                            <input id='maxiter' type="number" class="form-control"
                                                onchange="javascript: if(Number(this.value) < Number(this.min)) this.value = this.min;"
                                                min="100" value="500" step="50">
                                        </div>
                                    </div>
                                </div>
                            </div><div class="col-4"></div>`;
        let semiOptions = `<div class="col-4">
                                <div class="card">
                                    <div class="card-header ">
                                        Set phase for each color channel<br>(Input 0~1 float: eg. 0.01 or
                                        0.99)
                                    </div>
                                    <div class="card-body">
                                        <div class="input-group mb-3">
                                            <div class="input-group-prepend">
                                                <span class="input-group-text bg-danger text-light">R</span>
                                            </div>
                                            <input id='color-R' type="number" class="form-control"
                                                onchange="javascript: if (this.value.length > this.maxLength) this.value = this.value.slice(0, this.maxLength); if(Number(this.value) > Number(this.max)) this.value = 1; if(Number(this.value) < Number(this.min)) this.value=0;"
                                                maxlength="4" min="0" max="1" step="0.01">
                                        </div>
                                        <div class="input-group mb-3">
                                            <div class="input-group-prepend">
                                                <span
                                                    class="input-group-text bg-success text-light">G</span>
                                            </div>
                                            <input id='color-G' type="number" class="form-control"
                                                onchange="javascript: if (this.value.length > this.maxLength) this.value = this.value.slice(0, this.maxLength); if(Number(this.value) > Number(this.max)) this.value = 1; if(Number(this.value) < Number(this.min)) this.value=0;"
                                                maxlength="4" min="0" max="1" step="0.01">
                                        </div>
                                        <div class="input-group mb-3">
                                            <div class="input-group-prepend">
                                                <span
                                                    class="input-group-text bg-primary text-light">B</span>
                                            </div>
                                            <input id="color-B" type="number" class="form-control"
                                                onchange="javascript: if (this.value.length > this.maxLength) this.value = this.value.slice(0, this.maxLength); if(Number(this.value) > Number(this.max)) this.value = 1; if(Number(this.value) < Number(this.min)) this.value=0;"
                                                maxlength="4" min="0" max="1" step="0.01">
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="card">
                                    <div class="card-header ">
                                        Set range of coordinates<br>(Input float: -2 &lt; x &lt; 1, -1 &lt;
                                        y &lt; 1)
                                    </div>
                                    <div class="card-body">
                                        <div class="input-group mb-3">
                                            <div class="input-group-prepend">
                                                <span class="input-group-text">x1</span>
                                            </div>
                                            <input id='x1' type="number" class="form-control"
                                                onchange="javascript: if (Number(this.value) > Number(this.max)) this.value = this.max; if(Number(this.value) < Number(this.min)) this.value = this.min;"
                                                min="-2" max="1" onchange="calY2()" onkeyup="calY2()">
                                        </div>
                                        <div class="input-group mb-3">
                                            <div class="input-group-prepend">
                                                <span class="input-group-text">x2</span>
                                            </div>
                                            <input id='x2' type="number" class="form-control"
                                                onchange="javascript: if (Number(this.value) > Number(this.max)) this.value = this.max; if(Number(this.value) < Number(this.min)) this.value = this.min;"
                                                min="-2" max="1" onchange="calY2()" onkeyup="calY2()">
                                        </div>
                                        <div class="input-group mb-3">
                                            <div class="input-group-prepend">
                                                <span class="input-group-text">y1</span>
                                            </div>
                                            <input id='y1' type="number" class="form-control"
                                                onchange="javascript: if (Number(this.value) > Number(this.max)) this.value = this.max; if(Number(this.value) < Number(this.min)) this.value = this.min;"
                                                min="-1" max="1" onchange="calY2()" onkeyup="calY2()">
                                        </div>
                                        <div class="input-group mb-3">
                                            <div class="input-group-prepend">
                                                <span class="input-group-text">y2</span>
                                            </div>
                                            <input id='y2' type="number" class="form-control" readonly>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="card">
                                    <div class="card-header ">
                                        Set the rest of the parameters
                                    </div>
                                    <div class="card-body">
                                        <div class="input-group mb-3">
                                            <div class="input-group-prepend">
                                                <span class="input-group-text">Iterations</span>
                                            </div>
                                            <input id='maxiter' type="number" class="form-control"
                                                onchange="javascript: if(Number(this.value) < Number(this.min)) this.value = this.min;"
                                                min="100" value="500" step="50">
                                        </div>
                                        <div class="input-group mb-3">
                                            <div class="input-group-prepend">
                                                <span class="input-group-text">StripeS</span>
                                            </div>
                                            <input id='stripeS' type="number" class="form-control"
                                                onchange="javascript: if (Number(this.value) > Number(this.max)) this.value = this.max; if(Number(this.value) < Number(this.min)) this.value = this.min;"
                                                min="0" max="32" step="1">
                                        </div>
                                        <div class="input-group mb-3">
                                            <div class="input-group-prepend">
                                                <span class="input-group-text">NCycle</span>
                                            </div>
                                            <input id='ncycle' type="number" class="form-control"
                                                onchange="javascript: if(Number(this.value) < Number(this.min)) this.value = this.min; if(Number(this.value) > Number(this.max)) this.value = this.max;"
                                                min="1" step="1" max="200">
                                        </div>
                                        <div class="input-group mb-3">
                                            <div class="input-group-prepend">
                                                <span class="input-group-text">StepS</span>
                                            </div>
                                            <input id='stepS' type="number" class="form-control"
                                                onchange="javascript: if(Number(this.value) < Number(this.min)) this.value = this.min; if(Number(this.value) > Number(this.max)) this.value = this.max;"
                                                min="0" max="100" step="1">
                                        </div>
                                    </div>
                                </div>
                            </div>`;
        let rangeOptions = `<div class="col-4">
                                <div class="card">
                                    <div class="card-header ">
                                        Set phase for each color channel<br>(Input 0~1 float: eg. 0.01 or
                                        0.99)
                                    </div>
                                    <div class="card-body">
                                        <div class="input-group mb-3">
                                            <div class="input-group-prepend">
                                                <span class="input-group-text bg-danger text-light">R</span>
                                            </div>
                                            <input id='color-R' type="number" class="form-control"
                                                onchange="javascript: if (this.value.length > this.maxLength) this.value = this.value.slice(0, this.maxLength); if(Number(this.value) > Number(this.max)) this.value = 1; if(Number(this.value) < Number(this.min)) this.value=0;"
                                                maxlength="4" min="0" max="1" step="0.01">
                                        </div>
                                        <div class="input-group mb-3">
                                            <div class="input-group-prepend">
                                                <span
                                                    class="input-group-text bg-success text-light">G</span>
                                            </div>
                                            <input id='color-G' type="number" class="form-control"
                                                onchange="javascript: if (this.value.length > this.maxLength) this.value = this.value.slice(0, this.maxLength); if(Number(this.value) > Number(this.max)) this.value = 1; if(Number(this.value) < Number(this.min)) this.value=0;"
                                                maxlength="4" min="0" max="1" step="0.01">
                                        </div>
                                        <div class="input-group mb-3">
                                            <div class="input-group-prepend">
                                                <span
                                                    class="input-group-text bg-primary text-light">B</span>
                                            </div>
                                            <input id="color-B" type="number" class="form-control"
                                                onchange="javascript: if (this.value.length > this.maxLength) this.value = this.value.slice(0, this.maxLength); if(Number(this.value) > Number(this.max)) this.value = 1; if(Number(this.value) < Number(this.min)) this.value=0;"
                                                maxlength="4" min="0" max="1" step="0.01">
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="card">
                                    <div class="card-header ">
                                        Set the rest of the parameters
                                    </div>
                                    <div class="card-body">
                                        <div class="input-group mb-3">
                                            <div class="input-group-prepend">
                                                <span class="input-group-text">Iterations</span>
                                            </div>
                                            <input id='maxiter' type="number" class="form-control"
                                                onchange="javascript: if(Number(this.value) < Number(this.min)) this.value = this.min;"
                                                min="100" value="500" step="50">
                                        </div>
                                        <div class="input-group mb-3">
                                            <div class="input-group-prepend">
                                                <span class="input-group-text">StripeS</span>
                                            </div>
                                            <input id='stripeS' type="number" class="form-control"
                                                onchange="javascript: if (Number(this.value) > Number(this.max)) this.value = this.max; if(Number(this.value) < Number(this.min)) this.value = this.min;"
                                                min="0" max="32" step="1">
                                        </div>
                                        <div class="input-group mb-3">
                                            <div class="input-group-prepend">
                                                <span class="input-group-text">NCycle</span>
                                            </div>
                                            <input id='ncycle' type="number" class="form-control"
                                                onchange="javascript: if(Number(this.value) < Number(this.min)) this.value = this.min; if(Number(this.value) > Number(this.max)) this.value = this.max;"
                                                min="1" step="1" max="200">
                                        </div>
                                        <div class="input-group mb-3">
                                            <div class="input-group-prepend">
                                                <span class="input-group-text">StepS</span>
                                            </div>
                                            <input id='stepS' type="number" class="form-control"
                                                onchange="javascript: if(Number(this.value) < Number(this.min)) this.value = this.min; if(Number(this.value) > Number(this.max)) this.value = this.max;"
                                                min="0" max="100" step="1">
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="card">
                                    <div class="card-header ">
                                        Set the coordinate range for searching the Mandelbrot set image.
                                    </div>
                                    <div class="card-body">
                                        <div class="pb-3">
                                            <button id="selectRange" class="btn btn-primary btn-lg" onclick="selectRange()">
                                                Select Range
                                            </button>
                                        </div>
                                        <div class="input-group mb-3">
                                            <div class="input-group-prepend">
                                                <span class="input-group-text">x1</span>
                                            </div>
                                            <input id='x1' type="number" class="form-control" readonly>
                                        </div>
                                        <div class="input-group mb-3">
                                            <div class="input-group-prepend">
                                                <span class="input-group-text">x2</span>
                                            </div>
                                            <input id='x2' type="number" class="form-control" readonly>
                                        </div>
                                        <div class="input-group mb-3">
                                            <div class="input-group-prepend">
                                                <span class="input-group-text">y1</span>
                                            </div>
                                            <input id='y1' type="number" class="form-control" readonly>
                                        </div>
                                        <div class="input-group mb-3">
                                            <div class="input-group-prepend">
                                                <span class="input-group-text">y2</span>
                                            </div>
                                            <input id='y2' type="number" class="form-control" readonly>
                                        </div>
                                    </div>
                                </div>
                            </div>`;
        if (val == 'semi') {
            $('#optionPanel7').html(semiOptions);
        }
        else if (val == 'auto') {
            $('#optionPanel7').html(autoOptions);
        }
        else if (val == 'range') {
            $('#optionPanel7').html(rangeOptions);
        }
    });

    $('#generate3').on('click', () => {
        mode = $('input[name="modeSwitch"]').filter(':checked').val();
        if (mode == 'auto') {
            let data = {
                mode: 'auto',
                repeatNum: $('#repeatNum3').val(),
                maxiter: $('#maxiter').val(),
                uploadURL: $('#uploadURL2').val(),
                imgResolution: $('#imgResolution').val(),
            };

            if (data.maxiter == '' || data.uploadURL == '') {
                alert('Missing at coordinate or rest parameter');
            }
            else {
                $('#generate3').prop('disabled', true);
                $('#optionPanel9 .progress-bar').addClass('progress-bar-animated');
                $('#reset3').prop('disabled', true);
                eel.generateFractal(JSON.stringify(data))(r => {
                    if(r == 'success') {
                        $('#optionPanel9 .progress-bar').removeClass('progress-bar-animated');
                        $('#reset3').prop('disabled', false);
                        $('#generate3').prop('disabled', false);
                    }
                });
            }
        }
        else if (mode == 'semi') {
            let data = {
                mode: 'semi',
                repeatNum: $('#repeatNum3').val(),
                color: {
                    r: $('#color-R').val(),
                    g: $('#color-G').val(),
                    b: $('#color-B').val(),
                },
                coord: {
                    x1: $('#x1').val(),
                    x2: $('#x2').val(),
                    y1: $('#y1').val(),
                    y2: $('#y2').val(),
                },
                maxiter: $('#maxiter').val(),
                stripeS: $('#stripeS').val(),
                ncycle: $('#ncycle').val(),
                stepS: $('#stepS').val(),
                uploadURL: $('#uploadURL2').val(),
                imgResolution: $('#imgResolution').val(),
            };
            if (data.coord.x1 == '' || data.coord.x2 == '' || data.coord.y1 == '' || data.coord.y2 == '' || data.maxiter == '' || data.uploadURL == '') {
                alert('Missing at coordinate or rest parameter');
            } else {
                $('#generate3').prop('disabled', true);
                $('#optionPanel9 .progress-bar').addClass('progress-bar-animated');
                $('#reset3').prop('disabled', true);
                eel.generateFractal(JSON.stringify(data))(r => {
                    if(r == 'success') {
                        $('#optionPanel9 .progress-bar').removeClass('progress-bar-animated');
                        $('#reset3').prop('disabled', false);
                        $('#generate3').prop('disabled', false);
                    }
                });
            }
        }
        else if (mode == 'range') {
            let data = {
                mode: 'range',
                repeatNum: $('#repeatNum3').val(),
                color: {
                    r: $('#color-R').val(),
                    g: $('#color-G').val(),
                    b: $('#color-B').val(),
                },
                coord: {
                    x1: $('#x1').val(),
                    x2: $('#x2').val(),
                    y1: $('#y1').val(),
                    y2: $('#y2').val(),
                },
                maxiter: $('#maxiter').val(),
                stripeS: $('#stripeS').val(),
                ncycle: $('#ncycle').val(),
                stepS: $('#stepS').val(),
                uploadURL: $('#uploadURL2').val(),
                imgResolution: $('#imgResolution').val(),
            };
            if (data.coord.x1 == '' || data.coord.x2 == '' || data.coord.y1 == '' || data.coord.y2 == '' || data.maxiter == '' || data.uploadURL == '') {
                alert('Missing at coordinate or rest parameter');
            } else {
                $('#generate3').prop('disabled', true);
                $('#optionPanel9 .progress-bar').addClass('progress-bar-animated');
                $('#reset3').prop('disabled', true);
                eel.generateFractal(JSON.stringify(data))(r => {
                    if(r == 'success') {
                        $('#optionPanel9 .progress-bar').removeClass('progress-bar-animated');
                        $('#reset3').prop('disabled', false);
                        $('#generate3').prop('disabled', false);
                    }
                });
            }
        }
    });

    $('#reset3').on('click', () => {
        document.location.reload();
    });
});

selectRange = () => {
    eel.getRange()(r => {
        $('#x1').val(JSON.parse(r)[0]);
        $('#x2').val(JSON.parse(r)[1]);
        $('#y1').val(JSON.parse(r)[2]);
        $('#y2').val(JSON.parse(r)[3]);
    });
}

calY2 = () => {
    x1 = $('#x1').val();
    x2 = $('#x2').val();
    y1 = $('#y1').val();
    y2 = '';
    if (x1 != '' && x2 != '' && y1 != '') {
        y2 = ((1 / 1) * (Number(x2) - Number(x1)) + Number(y1)).toString();
    }
    $('#y2').val(y2);
}

