$(function ($) {

    function AjaxCall(dataObj) {
        setRequestHeader()
        $.ajax({
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            type: 'POST',
            url: "/utils/dashboard-setting/",
            data: dataObj,
            success: function (response) {
                // console.log("*** response: ", response, " ***")
            },
            error: function (response) {
                console.log("*** error response: ", response, " ***")
            }
        })
    }

    $(".translation-config").click(function () {
        let value = $(this).is(":checked")
        let settingObj = {
            "setting-object": {
                key: "translation-config",
                value: value
            }
        }
        AjaxCall(dataObj = JSON.stringify(settingObj))
    });

    $(".auto-translation-config").click(function () {
        let value = $(this).is(":checked")
        let settingObj = {
            "setting-object": {
                key: "auto-translation-config",
                value: value
            }
        }
        AjaxCall(dataObj = JSON.stringify(settingObj))
    });

    $(".skin-config").click(function () {
        let value = $(this).val()
        let settingObj = {
            "setting-object": {
                key: "skin-config",
                value: value
            }
        }
        AjaxCall(dataObj = JSON.stringify(settingObj))
    });

    $(".menu-collapsed-config").click(function () {
        let value = $(this).is(":checked")
        let settingObj = {
            "setting-object": {
                key: "menu-collapsed-config",
                value: value
            }
        }
        AjaxCall(dataObj = JSON.stringify(settingObj))
    });

    $(".layout-width-config").click(function () {
        let value = $(this).val()
        let settingObj = {
            "setting-object": {
                key: "layout-width-config",
                value: value
            }
        }
        AjaxCall(dataObj = JSON.stringify(settingObj))
    });

    $(".navbar-color-config").click(function () {
        let value = $(this).attr("data-navbar-color")
        let settingObj = {
            "setting-object": {
                key: "navbar-color-config",
                value: value
            }
        }
        AjaxCall(dataObj = JSON.stringify(settingObj))
    });

    $(".navbar-type-config").click(function () {
        let value = $(this).val()
        let settingObj = {
            "setting-object": {
                key: "navbar-type-config",
                value: value
            }
        }
        AjaxCall(dataObj = JSON.stringify(settingObj))
    });

    $(".footer-type-config").click(function () {
        let value = $(this).val()
        let settingObj = {
            "setting-object": {
                key: "footer-type-config",
                value: value
            }
        }
        AjaxCall(dataObj = JSON.stringify(settingObj))
    });

});