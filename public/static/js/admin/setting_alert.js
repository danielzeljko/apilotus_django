jQuery(document).ready(function($) {
    function get_login_user() {
        $.ajax({
            type : "GET",
            url : "../daemon/ajax_admin/get_login_user.php",
            data : {},
            success : function(data) {
                var user_info = jQuery.parseJSON(data);
                user_role = parseInt(user_info[2]);
                get_setting_alert_type();
            },
            failure : function(status) {
            }
        });
    }

    function show_alert(type, msg) {
        if ("level" == type) {
            $(".setting_crm_alert").html(msg);
            $(".setting_crm_alert").fadeIn(1e3, function() {
                $(".setting_crm_alert").fadeOut(3e3);
            });
        }
        else if ("level_edit" == type) {
            $(".alert_edit_level").html(msg);
            $(".alert_edit_level").fadeIn(1e3, function() {
                $(".alert_edit_level").fadeOut(3e3);
            });
        }
        else if ("receiver" == type) {
            $(".setting_receiver_alert").html(msg);
            $(".setting_receiver_alert").fadeIn(1e3, function() {
                $(".setting_receiver_alert").fadeOut(3e3);
            });
        }
        else if ("receiver_add" == type) {
            $(".receiver_add_alert").html(msg);
            $(".receiver_add_alert").fadeIn(1e3, function() {
                $(".receiver_add_alert").fadeOut(3e3);
            });
        } else if ("receiver_edit" == type) {
            $(".receiver_edit_alert").html(msg);
            $(".receiver_edit_alert").fadeIn(1e3, function() {
                $(".receiver_edit_alert").fadeOut(3e3);
            });
        }
    }

    function show_waiting(type, msg) {
        if ("level" == type) {
            if (level_wait = msg) {
                $(".alert_level_waiting").html(loading_icon);
            } else {
                $(".alert_level_waiting").html("");
            }
        }
        else if ("receiver" == type) {
            if (receiver_wait = msg) {
                $(".alert_receiver_waiting").html(loading_icon);
            } else {
                $(".alert_receiver_waiting").html("");
            }
        }
    }

    function get_setting_alert_type() {
        $.ajax({
            type : "GET",
            url : "../daemon/ajax_admin/setting_alert_type.php",
            data : {},
            success : function(data) {
                if ("error" == data) {
                    show_alert("level", "Cannot load Alert Type list.");
                }
                else if ("no_cookie" == data) {
                    window.location.href = "../../admin/login.php";
                }
                else {
                    alert_types = jQuery.parseJSON(data);
                    var html = "";
                    for (var i = 0; i < alert_types.length; i++) {
                        html += "<tr>";
                        html += "<td>" + alert_types[i][1] + "</td>";
                        html += "<td>" + alert_types[i][2] + "</td>";
                        html += "<td>" + alert_types[i][3] + "</td>";
                        html += "<td>" + alert_types[i][4] + "</td>";
                        var schedule = "";
                        if ("" != alert_types[i][5]) {
                            schedule += alert_types[i][5];
                        }
                        if ("" != alert_types[i][6]) {
                            if ("" != schedule) {
                                schedule += " ";
                            }
                            schedule += "(" + alert_types[i][6] + " hour)";
                        }
                        if ("1" == alert_types[i][7]) {
                            if ("" != schedule) {
                                schedule += ", ";
                            }
                            schedule += "SMS";
                        }
                        if ("1" == alert_types[i][8]) {
                            if ("" != schedule) {
                                schedule += ", ";
                            }
                            schedule += "Email";
                        }
                        if ("1" == alert_types[i][9]) {
                            if ("" != schedule) {
                                schedule += ", ";
                            }
                            schedule += "Telegram Bot";
                        }
                        html += "<td>" + schedule + "</td>";
                        html += '<td><button type="button" class="btn btn-link btn-sm btn_type_edit" id="' + alert_types[i][1] + '" data-toggle="modal" data-target="#type_edit_modal"><span class="glyphicon glyphicon-time" aria-hidden="true"></span>&nbsp;Schedule</button></td>';
                        html += "</tr>";
                    }
                    $(".table_type_body").html(html);
                    get_crm_list();
                }
            },
            failure : function() {
                show_waiting("level", false);
                show_alert("level", "Cannot load Alert Type list.");
            }
        });
    }

    function get_crm_list() {
        if (!level_wait) {
            show_waiting("level", true);
            var html = '<tr><th>#</th><th style="width:120px">CRM Name</th>';
            for (var i = 0; i < alert_types.length; i++) {
                if ("1" == alert_types[i][10]) {
                    html += "<th>" + alert_types[i][2] + "</th>";
                }
            }
            html += "<th>Action</th></tr>";
            $(".table_level_head").html(html);

            $.ajax({
                type : "GET",
                url : "../daemon/ajax_admin/crm_list.php",
                data : {},
                success : function(data) {
                    show_waiting("level", false);
                    if ("error" == data) {
                        show_alert("level", "Cannot load CRM list.");
                    }
                    else if ("no_cookie" == data) {
                        window.location.href = "../../admin/login.php";
                    }
                    else {
                        crm_list = jQuery.parseJSON(data);
                        var level_length = crm_list.length;
                        var html = "";
                        if (level_length > 0) {
                            for (var i = 0; i < level_length; i++) {
                                html += "<tr><td>" + (i + 1) + "</td>";
                                html += '<td id="name_' + crm_list[i][0] + '">' + crm_list[i][1] + "</td>";
                                for (var j = 0; j < alert_types.length; j++) {
                                    if ("1" == alert_types[j][10]) {
                                        html += '<td id="level_' + alert_types[j][1] + "_" + crm_list[i][0] + '"></td>';
                                    }
                                }
                                html += '<td><button type="button" class="btn btn-link btn-sm btn_level_edit" id="' + crm_list[i][0] + '" data-toggle="modal" data-target="#level_edit_modal"><span class="glyphicon glyphicon-edit" aria-hidden="true"></span>&nbsp;Edit</button></td>';
                                html += "</tr>";
                            }
                        } else {
                            show_alert("level", "There is no any crm data.");
                        }
                        $(".table_level_body").html(html);
                        for (i = 0; i < alert_types.length; i++) {
                            if ("1" == alert_types[i][10]) {
                                add_alert_levels(alert_types[i][1]);
                            }
                        }
                    }
                },
                failure : function() {
                    show_waiting("level", false);
                    show_alert("level", "Cannot load CRM list.");
                }
            });
        }
    }

    function add_alert_levels(alert_type) {
        $.ajax({
            type : "GET",
            url : "../daemon/ajax_admin/setting_alert_list.php",
            data : {
                alert_type : alert_type
            },
            success : function(data) {
                var alert_levels = jQuery.parseJSON(data);
                if ("error" == alert_levels[0]) {
                    show_alert("level", "Cannot load alert level information.");
                }
                else if ("no_cookie" == alert_levels[0]) {
                    window.location.href = "../../admin/login.php";
                }
                else {
                    for (var i = 0; i < alert_levels[2].length; i++) {
                        $("#level_" + alert_levels[2][i][2] + "_" + alert_levels[2][i][1]).html(alert_levels[2][i][4]);
                    }
                }
            },
            failure : function() {
                show_alert("level", "Cannot load alert level information.");
            }
        });
    }

    function setting_alert_edit(type, crm_id, level1, level2, is_last_alert) {
        $.ajax({
            type : "GET",
            url : "../daemon/ajax_admin/setting_alert_edit.php",
            data : {
                type : type,
                crm_id : crm_id,
                level1 : level1,
                level2 : level2
            },
            success : function(data) {
                if ("error" == data) {
                    show_alert("level", "Alert level cannot be changed.");
                }
                else if ("no_cookie" == data) {
                    window.location.href = "../../admin/login.php";
                }
                if (is_last_alert) {
                    get_crm_list();
                }
            },
            failure : function() {
                show_alert("level", "Alert level cannot be changed.");
            }
        });
    }

    function setting_schedule_edit(type, days, hours, sms, email, bot) {
        $.ajax({
            type : "GET",
            url : "../daemon/ajax_admin/setting_schedule_edit.php",
            data : {
                type : type,
                days : days,
                hours : hours,
                sms : sms,
                email : email,
                bot : bot
            },
            success : function(data) {
                if ("error" == data) {
                    show_alert("level", "Alert Schedule cannot be changed.");
                }
                else if ("no_cookie" == data) {
                    window.location.href = "../../admin/login.php";
                }
                else {
                    get_setting_alert_type();
                }
            },
            failure : function() {
                show_alert("level", "Alert Schedule cannot be changed.");
            }
        });
    }

    function setting_receiver_list() {
        show_waiting("receiver", true);
        $.ajax({
            type : "GET",
            url : "../daemon/ajax_admin/setting_receiver_list.php",
            data : {},
            success : function(data) {
                var textWas = jQuery.parseJSON(data);
                if (show_waiting("receiver", false), "error" != textWas[0]) {
                    if ("no_cookie" != textWas[0]) {
                        var keywordResults = textWas[1];
                        /** @type {string} */
                        var scrolltable = "";
                        /** @type {string} */
                        var option_code = "";
                        /** @type {string} */
                        var options_code = "";
                        /** @type {number} */
                        var o = 0;
                        /** @type {number} */
                        var _ = 0;
                        /** @type {number} */
                        var c = 0;
                        /** @type {number} */
                        var i = 0;
                        for (; i < keywordResults.length; i++) {
                            if ("0" == keywordResults[i][1]) {
                                /** @type {string} */
                                scrolltable = scrolltable + "<tr>";
                                /** @type {string} */
                                scrolltable = scrolltable + ("<td>" + ++o + "</td>");
                                /** @type {string} */
                                scrolltable = scrolltable + ('<td id="name1_' + keywordResults[i][0] + '" style="word-wrap:break-word;word-break:break-all;">' + keywordResults[i][2] + "</td>");
                                /** @type {string} */
                                scrolltable = scrolltable + ('<td id="stts1_' + keywordResults[i][0] + '">' + ("1" == keywordResults[i][3] ? "Enable" : "Disable") + "</td>");
                                if (9 == user_role) {
                                    /** @type {string} */
                                    scrolltable = scrolltable + "<td>";
                                    /** @type {string} */
                                    scrolltable = scrolltable + ('<button type="button" class="btn btn-link btn-sm btn_receiver_sms_edit" id="' + keywordResults[i][0] + '" data-toggle="modal" data-target="#receiver_edit_modal"><span class="glyphicon glyphicon-edit" aria-hidden="true"></span></button>');
                                    /** @type {string} */
                                    scrolltable = scrolltable + ('<button type="button" class="btn btn-link btn-sm btn_receiver_sms_delete" id="' + keywordResults[i][0] + '" data-toggle="modal" data-target="#receiver_delete_modal"><span class="glyphicon glyphicon-minus-sign" aria-hidden="true" style="color: #ffa5a5"></span></button>');
                                    /** @type {string} */
                                    scrolltable = scrolltable + "</td>";
                                }
                                /** @type {string} */
                                scrolltable = scrolltable + "</tr>";
                            } else {
                                if ("1" == keywordResults[i][1]) {
                                    /** @type {string} */
                                    option_code = option_code + "<tr>";
                                    /** @type {string} */
                                    option_code = option_code + ("<td>" + ++_ + "</td>");
                                    /** @type {string} */
                                    option_code = option_code + ('<td id="name2_' + keywordResults[i][0] + '" style="word-wrap:break-word;word-break:break-all;">' + keywordResults[i][2] + "</td>");
                                    /** @type {string} */
                                    option_code = option_code + ('<td id="stts2_' + keywordResults[i][0] + '">' + ("1" == keywordResults[i][3] ? "Enable" : "Disable") + "</td>");
                                    if (9 == user_role) {
                                        /** @type {string} */
                                        option_code = option_code + "<td>";
                                        /** @type {string} */
                                        option_code = option_code + ('<button type="button" class="btn btn-link btn-sm btn_receiver_mail_edit" id="' + keywordResults[i][0] + '" data-toggle="modal" data-target="#receiver_edit_modal"><span class="glyphicon glyphicon-edit" aria-hidden="true"></span></button>');
                                        /** @type {string} */
                                        option_code = option_code + ('<button type="button" class="btn btn-link btn-sm btn_receiver_mail_delete" id="' + keywordResults[i][0] + '" data-toggle="modal" data-target="#receiver_delete_modal"><span class="glyphicon glyphicon-minus-sign" aria-hidden="true" style="color: #ffa5a5"></span></button>');
                                        /** @type {string} */
                                        option_code = option_code + "</td>";
                                    }
                                    /** @type {string} */
                                    option_code = option_code + "</tr>";
                                } else {
                                    if ("2" == keywordResults[i][1]) {
                                        /** @type {string} */
                                        options_code = options_code + "<tr>";
                                        /** @type {string} */
                                        options_code = options_code + ("<td>" + ++c + "</td>");
                                        /** @type {string} */
                                        options_code = options_code + ('<td id="name3_' + keywordResults[i][0] + '" style="word-wrap:break-word;word-break:break-all;">' + keywordResults[i][2] + "</td>");
                                        /** @type {string} */
                                        options_code = options_code + ('<td id="chatid3_' + keywordResults[i][0] + '">' + keywordResults[i][4] + "</td>");
                                        /** @type {string} */
                                        options_code = options_code + ('<td id="stts3_' + keywordResults[i][0] + '">' + ("1" == keywordResults[i][3] ? "Enable" : "Disable") + "</td>");
                                        if (9 == user_role) {
                                            /** @type {string} */
                                            options_code = options_code + "<td>";
                                            /** @type {string} */
                                            options_code = options_code + ('<button type="button" class="btn btn-link btn-sm btn_receiver_bot_edit" id="' + keywordResults[i][0] + '" data-toggle="modal" data-target="#receiver_edit_modal"><span class="glyphicon glyphicon-edit" aria-hidden="true"></span></button>');
                                            /** @type {string} */
                                            options_code = options_code + ('<button type="button" class="btn btn-link btn-sm btn_receiver_bot_delete" id="' + keywordResults[i][0] + '" data-toggle="modal" data-target="#receiver_delete_modal"><span class="glyphicon glyphicon-minus-sign" aria-hidden="true" style="color: #ffa5a5"></span></button>');
                                            /** @type {string} */
                                            options_code = options_code + "</td>";
                                        }
                                        /** @type {string} */
                                        options_code = options_code + "</tr>";
                                    }
                                }
                            }
                        }
                        $(".table_receiver_sms_body").html(scrolltable);
                        $(".table_receiver_mail_body").html(option_code);
                        $(".table_receiver_bot_body").html(options_code);
                    } else {
                        /** @type {string} */
                        window.location.href = "../../admin/login.php";
                    }
                } else {
                    show_alert("receiver", "Cannot load alert receiver list.");
                }
            },
            failure : function(status) {
                show_waiting("account", false);
                show_alert("account", "Cannot load account list.");
            }
        });
    }
    /**
     * @param {number} input
     * @return {undefined}
     */
    function tasksAjaxCall(input) {
        show_waiting("receiver", true);
        /** @type {number} */
        var statusMock = 1;
        if ($(".add_receiver_state").prop("checked")) {
            /** @type {number} */
            statusMock = 0;
        }
        $.ajax({
            type : "GET",
            url : "../daemon/ajax_admin/setting_receiver_add.php",
            data : {
                type : input,
                address : $(".add_receiver_name").val(),
                chat_id : $(".add_receiver_chatid").val(),
                status : statusMock
            },
            success : function(status) {
                if (show_waiting("receiver", false), "success" == status) {
                    setting_receiver_list();
                } else {
                    if ("no_cookie" == status) {
                        return void(window.location.href = "../../admin/login.php");
                    }
                    show_alert("receiver", "Alert receiver cannot be added.");
                }
            },
            failure : function(status) {
                show_waiting("receiver", false);
                show_alert("receiver", "Alert receiver cannot be added.");
            }
        });
    }
    /**
     * @param {number} t
     * @return {undefined}
     */
    function graphPreview(t) {
        show_waiting("receiver", true);
        /** @type {number} */
        var statusMock = 1;
        if ($(".edit_receiver_state").prop("checked")) {
            /** @type {number} */
            statusMock = 0;
        }
        $.ajax({
            type : "GET",
            url : "../daemon/ajax_admin/setting_receiver_edit.php",
            data : {
                receiver_id : id2,
                type : t,
                address : $(".edit_receiver_name").val(),
                chat_id : $(".edit_receiver_chatid").val(),
                status : statusMock
            },
            success : function(status) {
                if (show_waiting("receiver", false), "success" == status) {
                    setting_receiver_list();
                } else {
                    if ("no_cookie" == status) {
                        return void(window.location.href = "../../admin/login.php");
                    }
                    show_alert("receiver", "Alert receiver cannot be changed.");
                }
            },
            failure : function(status) {
                show_waiting("receiver", false);
                show_alert("receiver", "Alert receiver cannot be changed.");
            }
        });
    }
    /**
     * @param {number} options
     * @return {undefined}
     */
    function getAsyncContent(options) {
        show_waiting("receiver", true);
        $.ajax({
            type : "GET",
            url : "../daemon/ajax_admin/setting_receiver_delete.php",
            data : {
                receiver_id : id2
            },
            success : function(status) {
                if (show_waiting("receiver", false), "success" == status) {
                    setting_receiver_list();
                } else {
                    if ("no_cookie" == status) {
                        return void(window.location.href = "../../admin/login.php");
                    }
                    show_alert("receiver", "Alert receiver cannot be deleted.");
                }
            },
            failure : function(status) {
                show_waiting("receiver", false);
                show_alert("receiver", "Alert receiver cannot be deleted.");
            }
        });
    }
    var crm_list;
    var alert_types;
    var item = -1;
    var request = -1;
    var id2 = -1;
    var icon = "";
    var user_role = 0;
    var level_wait = false;
    var receiver_wait = false;
    var loading_icon = '<img src="../images/loading.gif" style="width: 22px; height: 22px;">';

    get_login_user();
    $(".table_level_body").on("click", ".btn_level_edit", function(canCreateDiscussions) {
        item = $(this).prop("id");
        /** @type {string} */
        var scrolltable = "";
        /** @type {string} */
        scrolltable = scrolltable + '<div class="alert alert-warning alert_edit_level" role="alert" style="display:none"></div>';
        /** @type {string} */
        scrolltable = scrolltable + '<div class="row" style="margin-bottom:5px;">';
        /** @type {string} */
        scrolltable = scrolltable + '<div class="col-xs-6 modal_input_label">CRM Name</div>';
        /** @type {string} */
        scrolltable = scrolltable + ('<div class="col-xs-6"><input type="text" class="form-control input-sm edit_crm_name" readonly value="' + $("#name_" + item).text() + '"></div>');
        /** @type {string} */
        scrolltable = scrolltable + "</div>";
        /** @type {number} */
        var j = 0;
        for (; j < alert_types.length; j++) {
            if ("1" == alert_types[j][10]) {
                /** @type {string} */
                scrolltable = scrolltable + '<div class="row" style="margin-bottom:5px;">';
                /** @type {string} */
                scrolltable = scrolltable + ('<div class="col-xs-6 modal_input_label">' + alert_types[j][2] + "</div>");
                /** @type {string} */
                scrolltable = scrolltable + ('<div class="col-xs-6"><input type="text" class="form-control input-sm edit_level_' + alert_types[j][1] + '" value="' + $("#level_" + alert_types[j][1] + "_" + item).text() + '"></div>');
                /** @type {string} */
                scrolltable = scrolltable + "</div>";
            }
        }
        $(".modal_level_body").html(scrolltable);
    });
    $(".modal_btn_level_edit").click(function() {
        for (var i = 0; i < alert_types.length; i++) {
            if ("1" == alert_types[i][10] && "" == $(".edit_level_" + alert_types[i][1]).val()) {
                show_alert("level_edit", "Please input Alert level.");
                $(".edit_level_" + alert_types[i][1]).focus();
                return;
            }
        }
        $("#level_edit_modal").modal("toggle");

        var is_last_item = 0;
        for (i = 0; i < alert_types.length; i++) {
            if ("1" == alert_types[i][10]) {
                is_last_item = i;
            }
        }
        for (i = 0; i < alert_types.length; i++) {
            if ("1" == alert_types[i][10]) {
                setting_alert_edit(alert_types[i][1], item, $(".edit_level_" + alert_types[i][1]).val(), "0", is_last_item == i);
            }
        }
    });
    $(".table_type_body").on("click", ".btn_type_edit", function(canCreateDiscussions) {
        request = $(this).prop("id");
        $(".edit_day").each(function(canCreateDiscussions) {
            $(this).prop("checked", false);
        });
        $(".edit_hour").each(function(canCreateDiscussions) {
            $(this).prop("checked", false);
        });
        $(".edit_receiver").each(function(canCreateDiscussions) {
            $(this).prop("checked", false);
        });
        /** @type {number} */
        var j = 0;
        for (; j < alert_types.length; j++) {
            if (request == alert_types[j][1]) {
                var serverElements = alert_types[j][5].split(",");
                var spheres = alert_types[j][6].split(",");
                var d = alert_types[j][7];
                var l = alert_types[j][8];
                var n = alert_types[j][9];
                /** @type {number} */
                var i = 0;
                for (; i < serverElements.length; i++) {
                    $("#day_" + serverElements[i]).prop("checked", true);
                }
                /** @type {number} */
                var iter_sph = 0;
                for (; iter_sph < spheres.length; iter_sph++) {
                    $("#hour_" + spheres[iter_sph]).prop("checked", true);
                }
                return "1" == d && $("#receiver_0").prop("checked", true), "1" == l && $("#receiver_1").prop("checked", true), void("1" == n && $("#receiver_2").prop("checked", true));
            }
        }
    });
    $(".modal_btn_type_edit").click(function() {
        /** @type {string} */
        var name = "";
        $(".edit_day").each(function(i) {
            if ($(this).prop("checked")) {
                if ("" != name) {
                    name = name + ",";
                }
                name = name + $(this).prop("id").substring(4);
            }
        });
        /** @type {string} */
        var value = "";
        $(".edit_hour").each(function(canCreateDiscussions) {
            if ($(this).prop("checked")) {
                if ("" != value) {
                    value = value + ",";
                }
                value = value + $(this).prop("id").substring(5);
            }
        });
        /** @type {string} */
        var info = $("#receiver_0").prop("checked") ? "1" : "0";
        /** @type {string} */
        var parent = $("#receiver_1").prop("checked") ? "1" : "0";
        /** @type {string} */
        var secret = $("#receiver_2").prop("checked") ? "1" : "0";
        $("#type_edit_modal").modal("toggle");
        setting_schedule_edit(request, name, value, info, parent, secret);
    });
    $(".btn_receiver_sms_add").click(function() {
        /** @type {string} */
        icon = "sms";
        $(".add_receiver_label").html("SMS Number");
        $(".add_receiver_name").val("");
        $(".add_receiver_chatid").val("");
        $(".add_receiver_state").prop("checked", false);
        $("#telegram_add_chatid").css("display", "none");
    });
    $(".modal_btn_receiver_add").click(function() {
        if ("sms" == icon) {
            if ("" == $(".add_receiver_name").val()) {
                return show_alert("receiver_add", "Please input SMS Number."), void $(".add_receiver_name").focus();
            }
            tasksAjaxCall(0);
        } else {
            if ("mail" == icon) {
                if ("" == $(".add_receiver_name").val()) {
                    return show_alert("receiver_add", "Please input Email Address."), void $(".add_receiver_name").focus();
                }
                tasksAjaxCall(1);
            } else {
                if ("bot" == icon) {
                    if ("" == $(".add_receiver_name").val()) {
                        return show_alert("receiver_add", "Please input User Name."), void $(".add_receiver_name").focus();
                    }
                    if ("" == $(".add_receiver_chatid").val()) {
                        return show_alert("receiver_add", "Please input Chat ID."), void $(".add_receiver_chatid").focus();
                    }
                    tasksAjaxCall(2);
                }
            }
        }
        $("#receiver_add_modal").modal("toggle");
    });
    $(".table_receiver_sms_body").on("click", ".btn_receiver_sms_edit", function(canCreateDiscussions) {
        /** @type {string} */
        icon = "sms";
        id2 = $(this).prop("id");
        $(".edit_receiver_label").html("SMS Number");
        $(".edit_receiver_name").val($("#name1_" + id2).text());
        if ("Disable" == $("#stts1_" + id2).text()) {
            $(".edit_receiver_state").prop("checked", true);
        } else {
            $(".edit_receiver_state").prop("checked", false);
        }
        $(".edit_receiver_chatid").val("");
        $("#telegram_edit_chatid").css("display", "none");
    });
    $(".modal_btn_receiver_edit").click(function() {
        if ("sms" == icon) {
            if ("" == $(".edit_receiver_name").val()) {
                return show_alert("receiver_edit", "Please input SMS Number."), void $(".edit_receiver_name").focus();
            }
            graphPreview(0);
        } else {
            if ("mail" == icon) {
                if ("" == $(".edit_receiver_name").val()) {
                    return show_alert("receiver_edit", "Please input Email Address."), void $(".edit_receiver_name").focus();
                }
                graphPreview(1);
            } else {
                if ("bot" == icon) {
                    if ("" == $(".edit_receiver_name").val()) {
                        return show_alert("receiver_edit", "Please input User Name."), void $(".edit_receiver_name").focus();
                    }
                    if ("" == $(".edit_receiver_chatid").val()) {
                        return show_alert("receiver_edit", "Please input Chat ID."), void $(".edit_receiver_chatid").focus();
                    }
                    graphPreview(2);
                }
            }
        }
        $("#receiver_edit_modal").modal("toggle");
    });
    $(".table_receiver_sms_body").on("click", ".btn_receiver_sms_delete", function(canCreateDiscussions) {
        /** @type {string} */
        icon = "sms";
        id2 = $(this).prop("id");
    });
    $(".modal_btn_receiver_delete").click(function() {
        $("#receiver_delete_modal").modal("toggle");
        if ("sms" == icon) {
            getAsyncContent(0);
        } else {
            if ("mail" == icon) {
                getAsyncContent(1);
            } else {
                if ("bot" == icon) {
                    getAsyncContent(2);
                }
            }
        }
    });
    $(".btn_receiver_mail_add").click(function() {
        /** @type {string} */
        icon = "mail";
        $(".add_receiver_label").html("Email Address");
        $(".add_receiver_name").val("");
        $(".add_receiver_state").prop("checked", false);
        $(".add_receiver_chatid").val("");
        $("#telegram_add_chatid").css("display", "none");
    });
    $(".table_receiver_mail_body").on("click", ".btn_receiver_mail_edit", function(canCreateDiscussions) {
        /** @type {string} */
        icon = "mail";
        id2 = $(this).prop("id");
        $(".edit_receiver_label").html("Email Address");
        $(".edit_receiver_name").val($("#name2_" + id2).text());
        if ("Disable" == $("#stts2_" + id2).text()) {
            $(".edit_receiver_state").prop("checked", true);
        } else {
            $(".edit_receiver_state").prop("checked", false);
        }
        $(".edit_receiver_chatid").val("");
        $("#telegram_edit_chatid").css("display", "none");
    });
    $(".table_receiver_mail_body").on("click", ".btn_receiver_mail_delete", function(canCreateDiscussions) {
        /** @type {string} */
        icon = "mail";
        id2 = $(this).prop("id");
    });
    $(".btn_receiver_bot_add").click(function() {
        /** @type {string} */
        icon = "bot";
        $(".add_receiver_label").html("User Name");
        $(".add_receiver_name").val("");
        $(".add_receiver_state").prop("checked", false);
        $(".add_receiver_chatid").val("");
        $("#telegram_add_chatid").css("display", "inherit");
    });
    $(".table_receiver_bot_body").on("click", ".btn_receiver_bot_edit", function(canCreateDiscussions) {
        /** @type {string} */
        icon = "bot";
        id2 = $(this).prop("id");
        $(".edit_receiver_label").html("User Name");
        $(".edit_receiver_name").val($("#name3_" + id2).text());
        if ("Disable" == $("#stts3_" + id2).text()) {
            $(".edit_receiver_state").prop("checked", true);
        } else {
            $(".edit_receiver_state").prop("checked", false);
        }
        $(".edit_receiver_chatid").val($("#chatid3_" + id2).text());
        $("#telegram_edit_chatid").css("display", "inherit");
    });
    $(".table_receiver_bot_body").on("click", ".btn_receiver_bot_delete", function(canCreateDiscussions) {
        /** @type {string} */
        icon = "bot";
        id2 = $(this).prop("id");
    });
});
