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