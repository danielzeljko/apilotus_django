'use strict';
jQuery(document).ready(function($) {

    function show_alert(value, msg) {
        if ("account" == value) {
            $(".setting_account_alert").html(msg);
            $(".setting_account_alert").fadeIn(1e3, function() {
                $(".setting_account_alert").fadeOut(3e3);
            });
        } else if ("account_add" == value) {
            $(".account_add_alert").html(msg);
            $(".account_add_alert").fadeIn(1e3, function () {
                $(".account_add_alert").fadeOut(3e3);
            });
        } else if ("account_edit" == value) {
            $(".account_edit_alert").html(msg);
            $(".account_edit_alert").fadeIn(1e3, function () {
                $(".account_edit_alert").fadeOut(3e3);
            });
        } else if ("account_password" == value) {
            $(".account_password_alert").html(msg);
            $(".account_password_alert").fadeIn(1e3, function () {
                $(".account_password_alert").fadeOut(3e3);
            });
        } else if ("blockip" == value) {
            $(".setting_ip_alert").html(msg);
            $(".setting_ip_alert").fadeIn(1e3, function () {
                $(".setting_ip_alert").fadeOut(3e3);
            });
        } else if ("blockip_modal" == value) {
            $(".block_ip_alert").html(msg);
            $(".block_ip_alert").fadeIn(1e3, function () {
                $(".block_ip_alert").fadeOut(3e3);
            });
        }
    }

    function show_waiting(type, success) {
        if ("account" == type) {
            if (loading = success) {
                $(".setting_account_waiting").html(loading_icon);
            } else {
                $(".setting_account_waiting").html("");
            }
        } else if ("blockip" == type) {
            if (success) {
                $(".setting_ip_waiting").html(loading_icon);
            } else {
                $(".setting_ip_waiting").html("");
            }
        }
    }

    function get_account_list() {
        if (!loading) {
            show_waiting("account", true);
            $.ajax({
                type : "GET",
                url : "../daemon/ajax_admin/setting_account_list.php",
                data : {},
                success : function(data) {
                    show_waiting("account", false);
                    if ("error" === data) {
                        show_alert("account", "Cannot load account list.");
                    }
                    else if ("no_cookie" === data) {
                        window.location.href = "../../admin/login.php";
                    }
                    else {
                        accounts = jQuery.parseJSON(data);
                        let accounts_length = accounts.length;
                        let html = "";
                        if (accounts_length > 0) {
                            for (let i = 0; i < accounts_length; i++) {
                                html += "<tr><td>" + (i + 1) + "</td>";
                                html += '<td id="name_' + accounts[i][0] + '">' + accounts[i][1] + "</td>";
                                html += '<td id="disp_' + accounts[i][0] + '">' + accounts[i][3] + "</td>";

                                // SMS, EMAIL, TELEGRAM BOT
                                if ("1" == accounts[i][10] || "" == accounts[i][7]) {
                                    html = html + ('<td id="sms_' + accounts[i][0] + '">' + accounts[i][7] + "</td>");
                                } else {
                                    html = html + ('<td id="sms_' + accounts[i][0] + '"><span class="payment_badge payment_badge_red">' + accounts[i][7] + "</span></td>");
                                }
                                if ("1" == accounts[i][11] || "" == accounts[i][8]) {
                                    html = html + ('<td id="email_' + accounts[i][0] + '">' + accounts[i][8] + "</td>");
                                } else {
                                    html = html + ('<td id="email_' + accounts[i][0] + '"><span class="payment_badge payment_badge_red" style="text-transform: none">' + accounts[i][8] + "</span></td>");
                                }
                                if ("1" == accounts[i][12] || "" == accounts[i][9]) {
                                    html = html + ('<td id="bot_' + accounts[i][0] + '">' + accounts[i][9] + "</td>");
                                } else {
                                    html = html + ('<td id="bot_' + accounts[i][0] + '"><span class="payment_badge payment_badge_red">' + accounts[i][9] + "</span></td>");
                                }

                                // User Role
                                if ("9" == accounts[i][4])
                                    html = html + ('<td id="role_' + accounts[i][0] + '">Administrator</td>');
                                else if ("1" == accounts[i][4])
                                    html = html + ('<td id="role_' + accounts[i][0] + '">Super User</td>');
                                else if ("0" == accounts[i][4])
                                    html = html + ('<td id="role_' + accounts[i][0] + '">Regular User</td>');
                                else
                                    html = html + ('<td id="role_' + accounts[i][0] + '">Unknown</td>');

                                // User Status
                                if ("1" == accounts[i][5]) {
                                    html = html + ('<td id="state_' + accounts[i][0] + '"><span class="payment_badge payment_badge_blue">Enable</span></td><td>');
                                } else {
                                    html = html + ('<td id="state_' + accounts[i][0] + '"><span class="payment_badge payment_badge_red">Disable</span></td><td>');
                                }
                                html = html + ('<button type="button" class="btn btn-link btn-sm setting_account_edit" id="' + accounts[i][0] + '" data-toggle="modal" data-target="#account_edit_modal"><span class="glyphicon glyphicon-edit" aria-hidden="true"></span>&nbsp;Edit</button>');
                                html = html + ('<button type="button" class="btn btn-link btn-sm setting_account_password" id="' + accounts[i][0] + '" data-toggle="modal" data-target="#account_password_modal"><span class="glyphicon glyphicon-lock" aria-hidden="true"></span>&nbsp;Password</button>');
                                if (9 === logged_in_user_role) {
                                    if ("0" === accounts[i][4])
                                        html = html + ('<button type="button" class="btn btn-link btn-sm setting_permission_edit" id="' + accounts[i][0] + '" data-toggle="modal" data-target="#permission_edit_modal"><span class="glyphicon glyphicon-th-list" aria-hidden="true"></span>&nbsp;Permission</button>');
                                    else if ("9" === accounts[i][4])
                                        html = html + ('<button type="button" class="btn btn-link btn-sm setting_permission_edit" id="' + accounts[i][0] + '" data-toggle="modal" data-target="#permission_edit_modal" disabled><span class="glyphicon glyphicon-th-list" aria-hidden="true"></span>&nbsp;Permission</button>');
                                    if (logged_in_user_id == accounts[i][0] || "0" === accounts[i][4])
                                        html = html + ('<button type="button" class="btn btn-link btn-sm setting_account_delete" id="' + accounts[i][0] + '" data-toggle="modal" data-target="#account_delete_modal"><span class="glyphicon glyphicon-minus-sign" aria-hidden="true" style="color: #ffa5a5"></span>&nbsp;Delete</button>');
                                    else
                                        html = html + ('<button type="button" class="btn btn-link btn-sm setting_account_delete" id="' + accounts[i][0] + '" data-toggle="modal" data-target="#account_delete_modal" disabled><span class="glyphicon glyphicon-minus-sign" aria-hidden="true" style="color: #ffa5a5"></span>&nbsp;Delete</button>');
                                }
                                html = html + "</td></tr>";
                            }
                        } else {
                            show_alert("account", "There is no any account data.");
                        }
                        $(".table_account_body").html(html);
                    }
                },
                failure : function() {
                    show_waiting("account", false);
                    show_alert("account", "Cannot load account list.");
                }
            });
        }
    }
    /**
     * @return {undefined}
     */
    function get_block_ip_list() {
        show_waiting("blockip", true);
        $.ajax({
            type : "GET",
            url : "../daemon/ajax_admin/setting_blockip_list.php",
            data : {},
            success : function(data) {
                if (show_waiting("blockip", false), "error" != data) {
                    if ("no_cookie" != data) {
                        var satIdList = jQuery.parseJSON(data);
                        /** @type {string} */
                        var scrolltable = "";
                        if (satIdList.length > 0) {
                            /** @type {number} */
                            var i = 0;
                            for (; i < satIdList.length; i++) {
                                /** @type {string} */
                                scrolltable = scrolltable + ("<tr><td>" + (i + 1) + "</td>");
                                /** @type {string} */
                                scrolltable = scrolltable + ('<td id="ipaddr_' + satIdList[i][0] + '">' + satIdList[i][1] + "</td>");
                                /** @type {string} */
                                scrolltable = scrolltable + ('<td id="ipdesc_' + satIdList[i][0] + '">' + satIdList[i][2] + "</td>");
                                if (9 === logged_in_user_role) {
                                    /** @type {string} */
                                    scrolltable = scrolltable + "<td>";
                                    /** @type {string} */
                                    scrolltable = scrolltable + ('<button type="button" class="btn btn-link btn-sm btn_blockip_edit" id="ipid_' + satIdList[i][0] + '" data-toggle="modal" data-target="#block_ip_modal"><span class="glyphicon glyphicon-edit" aria-hidden="true"></span>&nbsp;Edit</button>');
                                    /** @type {string} */
                                    scrolltable = scrolltable + ('<button type="button" class="btn btn-link btn-sm btn_blockip_delete" id="ipid_' + satIdList[i][0] + '" data-toggle="modal" data-target="#blockip_delete_modal"><span class="glyphicon glyphicon-minus-sign" aria-hidden="true" style="color: #ffa5a5"></span>&nbsp;Delete</button>');
                                    /** @type {string} */
                                    scrolltable = scrolltable + "</td>";
                                }
                                /** @type {string} */
                                scrolltable = scrolltable + "</tr>";
                            }
                        }
                        $(".table_blockip_body").html(scrolltable);
                    } else {
                        /** @type {string} */
                        window.location.href = "../../admin/login.php";
                    }
                } else {
                    show_alert("account", "Cannot load block IP list.");
                }
            },
            failure : function(status) {
                show_waiting("blockip", false);
                show_alert("blockip", "Cannot load block IP list.");
            }
        });
    }
    var accounts;
    /** @type {number} */
    var account_id = -1;
    /** @type {number} */
    var conid = -1;
    /** @type {number} */
    var logged_in_user_role = 0;
    var logged_in_user_id = 0;
    /** @type {boolean} */
    var loading = false;
    /** @type {string} */
    var loading_icon = '<img src="../images/loading.gif" style="width:22px;height:22px;">';
    /** @type {string} */
    var type = "";
    let crm_permission_len = 0;

    $.ajax({
        type : "GET",
        url : "../daemon/ajax_admin/get_login_user.php",
        data : {},
        success : function(data) {
            let logged_in_user = jQuery.parseJSON(data);
            logged_in_user_role = parseInt(logged_in_user[2]);
            logged_in_user_id = parseInt(logged_in_user[0]);
            get_account_list();
            get_block_ip_list();
        },
        failure : function() {
        }
    });
    $(".btn_account_add").click(function() {
        $(".add_user_name").val("");
        $(".add_password").val("");
        $(".add_repassword").val("");
        $(".add_display_name").val("");
        $(".add_sms_number").val("");
        $(".add_email_address").val("");
        $(".add_telegram_bot").val("");
        $(".add_role").prop("checked", false);
        $(".add_disable_account").prop("checked", false);
        $(".add_disable_sms").prop("checked", false);
        $(".add_disable_email").prop("checked", false);
        $(".add_disable_bot").prop("checked", false);
    });
    $(".modal_btn_account_add").click(function() {
        return "" == $(".add_user_name").val() ? (show_alert("account_add", "Please input User ID."), void $(".add_user_name").focus()) : "" == $(".add_password").val() ? (show_alert("account_add", "Please input Password."), void $(".add_password").focus()) : $(".add_password").val() != $(".add_repassword").val() ? (show_alert("account_add", "Doesn't match password."), void $(".add_repassword").focus()) : "" == $(".add_display_name").val() ? (show_alert("account_add", "Please input User Name."), void $(".add_display_name").focus()) :
            ($("#account_add_modal").modal("toggle"), void function() {
                show_waiting("account", true);
                /** @type {number} */
                var captureState = 1 == $(".add_disable_account").prop("checked") ? 0 : 1;
                /** @type {number} */
                var e = 1 == $(".add_disable_sms").prop("checked") ? 0 : 1;
                /** @type {number} */
                var n = 1 == $(".add_disable_email").prop("checked") ? 0 : 1;
                /** @type {number} */
                var o = 1 == $(".add_disable_bot").prop("checked") ? 0 : 1;
                $.ajax({
                    type : "GET",
                    url : "../daemon/ajax_admin/setting_account_add.php",
                    data : {
                        user_name : $(".add_user_name").val(),
                        password : $(".add_password").val(),
                        display_name : $(".add_display_name").val(),
                        sms : $(".add_sms_number").val(),
                        email : $(".add_email_address").val(),
                        bot : $(".add_telegram_bot").val(),
                        role : $(".add_role").val(),
                        state : captureState,
                        enable_sms : e,
                        enable_email : n,
                        enable_bot : o
                    },
                    success : function(status) {
                        if (show_waiting("account", false), "success" == status) {
                            get_account_list();
                        } else {
                            if ("no_cookie" == status) {
                                return void(window.location.href = "../../admin/login.php");
                            }
                            show_alert("account", "Account cannot be added.");
                        }
                    },
                    failure : function(status) {
                        show_waiting("account", false);
                        show_alert("account", "Account cannot be added.");
                    }
                });
            }());
    });
    $(".table_account_body").on("click", ".setting_account_edit", function(n) {
        account_id = $(this).prop("id");
        /** @type {number} */
        var i = 0;
        for (; i < accounts.length; i++) {
            if (account_id == accounts[i][0]) {
                $(".edit_user_name").val(accounts[i][1]);
                $(".edit_display_name").val(accounts[i][3]);
                $(".edit_role").val(accounts[i][4]);
                $(".edit_sms_number").val(accounts[i][7]);
                $(".edit_email_address").val(accounts[i][8]);
                $(".edit_telegram_bot").val(accounts[i][9]);
                $(".edit_disable_account").prop("checked", "1" != accounts[i][5]);
                $(".edit_disable_sms").prop("checked", "1" != accounts[i][10]);
                $(".edit_disable_email").prop("checked", "1" != accounts[i][11]);
                $(".edit_disable_bot").prop("checked", "1" != accounts[i][12]);
                break;
            }
        }
    });
    $(".modal_btn_account_edit").click(function() {
        return "" == $(".edit_user_name").val() ? (show_alert("account_edit", "Please input User ID."), void $(".edit_user_name").focus()) : "" == $(".edit_display_name").val() ? (show_alert("account_edit", "Please input User Name."), void $(".edit_display_name").focus()) : ($("#account_edit_modal").modal("toggle"), void function() {
            show_waiting("account", true);
            /** @type {number} */
            var captureState = 1 == $(".edit_disable_account").prop("checked") ? 0 : 1;
            /** @type {number} */
            var n = 1 == $(".edit_disable_sms").prop("checked") ? 0 : 1;
            /** @type {number} */
            var o = 1 == $(".edit_disable_email").prop("checked") ? 0 : 1;
            /** @type {number} */
            var d = 1 == $(".edit_disable_bot").prop("checked") ? 0 : 1;
            $.ajax({
                type : "GET",
                url : "../daemon/ajax_admin/setting_account_edit.php",
                data : {
                    account_id : account_id,
                    user_name : $(".edit_user_name").val(),
                    display_name : $(".edit_display_name").val(),
                    sms : $(".edit_sms_number").val(),
                    email : $(".edit_email_address").val(),
                    bot : $(".edit_telegram_bot").val(),
                    role : $(".edit_role").val(),
                    state : captureState,
                    enable_sms : n,
                    enable_email : o,
                    enable_bot : d
                },
                success : function(status) {
                    show_waiting("account", false);
                    if ("success" == status) {
                        get_account_list();
                    } else {
                        if ("no_cookie" == status) {
                            /** @type {string} */
                            window.location.href = "../../admin/login.php";
                        } else {
                            show_alert("account", "Account cannot be changed.");
                        }
                    }
                },
                failure : function(status) {
                    show_waiting("account", false);
                    show_alert("account", "Account cannot be changed.");
                }
            });
        }());
    });
    $(".table_account_body").on("click", ".setting_account_password", function(canCreateDiscussions) {
        account_id = $(this).prop("id");
        $(".edit_password").val("");
        $(".edit_repassword").val("");
    });
    $(".modal_btn_account_password").click(function() {
        return "" == $(".edit_password").val() ? (show_alert("account_password", "Please input New Password."), void $(".edit_password").focus()) : $(".edit_password").val() != $(".edit_repassword").val() ? (show_alert("account_password", "Doesn't match password."), void $(".edit_repassword").focus()) : ($("#account_password_modal").modal("toggle"), show_waiting("account", true), void $.ajax({
            type : "GET",
            url : "../daemon/ajax_admin/setting_account_password.php",
            data : {
                account_id : account_id,
                password : $(".edit_password").val()
            },
            success : function(status) {
                if (show_waiting("account", false), "success" == status) {
                    get_account_list();
                } else {
                    if ("no_cookie" == status) {
                        return void(window.location.href = "../../admin/login.php");
                    }
                    show_alert("account", "Account Password cannot be changed.");
                }
            },
            failure : function(status) {
                show_waiting("account", false);
                show_alert("account", "Account Password cannot be changed.");
            }
        }));
    });
    $(".table_account_body").on("click", ".setting_account_delete", function(canCreateDiscussions) {
        account_id = $(this).prop("id");
    });
    $(".modal_btn_account_delete").click(function() {
        $("#account_delete_modal").modal("toggle");
        show_waiting("account", true);
        $.ajax({
            type : "GET",
            url : "../daemon/ajax_admin/setting_account_delete.php",
            data : {
                account_id : account_id
            },
            success : function(status) {
                if (show_waiting("account", false), "success" == status) {
                    get_account_list();
                } else {
                    if ("no_cookie" == status) {
                        return void(window.location.href = "../../admin/login.php");
                    }
                    show_alert("account", "Account cannot be deleted.");
                }
            },
            failure : function(status) {
                show_waiting("account", false);
                show_alert("account", "Account cannot be deleted.");
            }
        });
    });

    $(".table_account_body").on("click", ".setting_permission_edit", function() {
        account_id = $(this).prop("id");
        $(".pcrm_disable_item").each(function() {
            $(this).prop("checked", true);
        });
        $(".pdisable_item").each(function() {
            $(this).prop("checked", true);
        });
        if (loading)
            return;
        show_waiting("account", true);
        $.ajax({
            type : "GET",
            url : "../daemon/ajax_admin/setting_permission_list.php",
            data : {
                account_id : account_id
            },
            success : function(data) {
                show_waiting("account", false);
                if ("error" == data) {
                    show_alert("account", "Cannot load account permission list.");
                }
                else if ("no_cookie" == data) {
                    window.location.href = "../../admin/login.php";
                }
                else {
                    let permission_data = jQuery.parseJSON(data);
                    let crm_permissions = permission_data[2];
                    let page_permissions = permission_data[3];
                    crm_permission_len = crm_permissions.length;

                    let html = "";
                    let count = 0;
                    for (let i = 0; i < crm_permission_len; i++) {
                        html += "<tr>";
                        html += "<td>" + crm_permissions[i][1] + "</td>";
                        if (1 === crm_permissions[i][2]) {
                            html += '<td><input id="pcrm_enable_' + crm_permissions[i][0] + '" type="radio" class="pcrm_enable_item" name="pcrm_radio_' + crm_permissions[i][0] + '" checked/></td>';
                            html += '<td><input type="radio" class="pcrm_disable_item" name="pcrm_radio_' + crm_permissions[i][0] + '"/></td>';
                            count++;
                        }
                        else {
                            html += '<td><input id="pcrm_enable_' + crm_permissions[i][0] + '" type="radio" class="pcrm_enable_item" name="pcrm_radio_' + crm_permissions[i][0] + '"/></td>';
                            html += '<td><input type="radio" class="pcrm_disable_item" name="pcrm_radio_' + crm_permissions[i][0] + '" checked/></td>';
                        }
                        html += "</tr>";
                    }
                    $(".table_permission_body").html(html);
                    $("#selected_perms_count").html(count + ' of ' + crm_permission_len + ' options');

                    if (page_permissions) {
                        page_permissions = page_permissions.split(',');
                        for (let i = 0; i < page_permissions.length; i++) {
                            $("#penable_" + page_permissions[i]).prop('checked', true);
                        }
                    }
                }
            },
            failure : function() {
                show_waiting("account", false);
                show_alert("account", "Cannot load account permission list.");
            }
        });
    });
    $(".modal_btn_permission_edit").click(function() {
        let crm_permissions = [];
        let page_permissions = [];
        $(".pcrm_enable_item").each(function() {
            if ($(this).prop("checked")) {
                crm_permissions.push($(this).prop("id").substring(12));
            }
        });
        $(".penable_item").each(function() {
            if ($(this).prop("checked")) {
                page_permissions.push($(this).prop("id").substring(8));
            }
        });
        $("#permission_edit_modal").modal("toggle");
        show_waiting("account", true);
        $.ajax({
            type : "GET",
            url : "../daemon/ajax_admin/setting_permission_edit.php",
            data : {
                account_id : account_id,
                permissions : crm_permissions.join(','),
                page_permissions: page_permissions.join(',')
            },
            success : function(data) {
                show_waiting("account", false);
                if ("error" == data)
                    show_alert("account", "CRM permission cannot be changed.");
                else if ("no_cookie" == data)
                    window.location.href = "../../admin/login.php";
            },
            failure : function() {
                show_waiting("account", false);
                show_alert("account", "CRM permission cannot be changed.");
            }
        });
    });

    $(".btn_blockip_add").click(function() {
        /** @type {string} */
        type = "add";
        $(".ip_address").val("");
        $(".ip_description").val("");
    });
    $(".modal_btn_blockip_apply").click(function() {
        if ("" == $(".ip_address").val()) {
            return show_alert("blockip_modal", "Please input IP Address."), void $(".ip_address").focus();
        }
        $("#block_ip_modal").modal("toggle");
        if ("add" == type) {
            show_waiting("blockip", true);
            $.ajax({
                type : "GET",
                url : "../daemon/ajax_admin/setting_blockip_add.php",
                data : {
                    block_ip : $(".ip_address").val(),
                    description : $(".ip_description").val()
                },
                success : function(status) {
                    if (show_waiting("blockip", false), "success" == status) {
                        get_block_ip_list();
                    } else {
                        if ("no_cookie" == status) {
                            return void(window.location.href = "../../admin/login.php");
                        }
                        show_alert("blockip", "Block IP cannot be added.");
                    }
                },
                failure : function(status) {
                    show_waiting("blockip", false);
                    show_alert("blockip", "Block IP cannot be added.");
                }
            });
        } else {
            if ("edit" == type) {
                show_waiting("blockip", true);
                $.ajax({
                    type : "GET",
                    url : "../daemon/ajax_admin/setting_blockip_edit.php",
                    data : {
                        ip_id : conid,
                        block_ip : $(".ip_address").val(),
                        description : $(".ip_description").val()
                    },
                    success : function(status) {
                        if (show_waiting("blockip", false), "success" == status) {
                            get_block_ip_list();
                        } else {
                            if ("no_cookie" == status) {
                                return void(window.location.href = "../../admin/login.php");
                            }
                            show_alert("blockip", "Block IP cannot be changed.");
                        }
                    },
                    failure : function(status) {
                        show_waiting("blockip", false);
                        show_alert("blockip", "Block IP cannot be changed.");
                    }
                });
            }
        }
    });
    $(".table_blockip_body").on("click", ".btn_blockip_edit", function(canCreateDiscussions) {
        /** @type {string} */
        type = "edit";
        conid = $(this).prop("id").substring(5);
        var encodedPW = $("#ipaddr_" + conid).html();
        var old_selected = $("#ipdesc_" + conid).html();
        $(".ip_address").val(encodedPW);
        $(".ip_description").val(old_selected);
    });
    $(".table_blockip_body").on("click", ".btn_blockip_delete", function(canCreateDiscussions) {
        conid = $(this).prop("id").substring(5);
    });
    $(".modal_btn_blockip_delete").click(function() {
        $("#blockip_delete_modal").modal("toggle");
        show_waiting("blockip", true);
        $.ajax({
            type : "GET",
            url : "../daemon/ajax_admin/setting_blockip_delete.php",
            data : {
                ip_id : conid
            },
            success : function(status) {
                if (show_waiting("blockip", false), "success" == status) {
                    get_block_ip_list();
                } else {
                    if ("no_cookie" == status) {
                        return void(window.location.href = "../../admin/login.php");
                    }
                    show_alert("blockip", "Block IP cannot be deleted.");
                }
            },
            failure : function(status) {
                show_waiting("blockip", false);
                show_alert("blockip", "Block IP cannot be deleted.");
            }
        });
    });

    $("#penable").click(function() {
        $(".pcrm_enable_item").each(function() {
            $(this).prop("checked", true);
        });
        $("#selected_perms_count").html(crm_permission_len + ' of ' + crm_permission_len + ' options');
    });
    $("#pdisable").click(function() {
        $(".pcrm_disable_item").each(function() {
            $(this).prop("checked", true);
        });
        $("#selected_perms_count").html('0 of ' + crm_permission_len + ' options');
    });
    $(".table_permission_body").on("click", ".pcrm_enable_item", function () {
        let count = 0;
        $(".pcrm_enable_item").each(function() {
            if ($(this).prop("checked")) {
                count++;
            }
        });
        $("#selected_perms_count").html(count + ' of ' + crm_permission_len + ' options');
    });
    $(".table_permission_body").on("click", ".pcrm_disable_item", function () {
        let count = 0;
        $(".pcrm_enable_item").each(function() {
            if ($(this).prop("checked")) {
                count++;
            }
        });
        $("#selected_perms_count").html(count + ' of ' + crm_permission_len + ' options');
    });

    $("#penable_1").click(function () {
        $("#penable_11").prop("checked", true);
        $("#penable_12").prop("checked", true);
    });
    $("#pdisable_1").click(function () {
        $("#pdisable_11").prop("checked", true);
        $("#pdisable_12").prop("checked", true);
    });

    $("#penable_2").click(function () {
        $("#penable_21").prop("checked", true);
        $("#penable_22").prop("checked", true);
    });
    $("#pdisable_2").click(function () {
        $("#pdisable_21").prop("checked", true);
        $("#pdisable_22").prop("checked", true);
    });

    $("#penable_3").click(function () {
        $("#penable_31").prop("checked", true);
        $("#penable_32").prop("checked", true);
        $("#penable_33").prop("checked", true);
    });
    $("#pdisable_3").click(function () {
        $("#pdisable_31").prop("checked", true);
        $("#pdisable_32").prop("checked", true);
        $("#pdisable_33").prop("checked", true);
    });

    $("#penable_4").click(function () {
        $("#penable_41").prop("checked", true);
        $("#penable_42").prop("checked", true);
        $("#penable_43").prop("checked", true);
        $("#penable_44").prop("checked", true);
    });
    $("#pdisable_4").click(function () {
        $("#pdisable_41").prop("checked", true);
        $("#pdisable_42").prop("checked", true);
        $("#pdisable_43").prop("checked", true);
        $("#pdisable_44").prop("checked", true);
    });
});
