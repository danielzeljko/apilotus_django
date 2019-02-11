jQuery(document).ready(function($) {
    function show_alert(type, msg) {
        if ("main" == type) {
            $(".setting_crm_alert").html(msg);
            $(".setting_crm_alert").fadeIn(1e3, function() {
                $(".setting_crm_alert").fadeOut(3e3);
            });
        }
        else if ("add" == type) {
            $(".crm_add_alert").html(msg);
            $(".crm_add_alert").fadeIn(1e3, function () {
                $(".crm_add_alert").fadeOut(3e3);
            });
        }
        else if ("edit" == type) {
            $(".crm_edit_alert").html(msg);
            $(".crm_edit_alert").fadeIn(1e3, function () {
                $(".crm_edit_alert").fadeOut(3e3);
            });
        }
        else if ("crm_password" == type) {
            $(".crm_password_alert").html(msg);
            $(".crm_password_alert").fadeIn(1e3, function () {
                $(".crm_password_alert").fadeOut(3e3);
            });
        }
        else if ("api_password" == type) {
            $(".api_password_alert").html(msg);
            $(".api_password_alert").fadeIn(1e3, function () {
                $(".api_password_alert").fadeOut(3e3);
            });
        }
    }

    function show_waiting(data) {
        if (is_waiting = data) {
            $(".setting_crm_waiting").html(loading_icon);
        } else {
            $(".setting_crm_waiting").html("");
        }
    }

    function get_all_crm_list() {
        if (!is_waiting) {
            show_waiting(true);
            $.ajax({
                type : "GET",
                url : "../daemon/ajax_admin/setting_crm_list.php",
                data : {},
                success : function(data) {
                    show_waiting(false);
                    if ("error" == data) {
                        show_alert("main", "Cannot load CRM list.");
                    }
                    else if ("no_cookie" == data) {
                        window.location.href = "../../admin/login.php";
                    }
                    else {
                        crm_list = jQuery.parseJSON(data);
                        let html = "";
                        if (crm_list.length > 0) {
                            for (let i = 0; i < crm_list.length; i++) {
                                html += "<tr><td>" + (i + 1) + "</td>";
                                html += '<td id="name_' + crm_list[i][0] + '">' + crm_list[i][1] + "</td>";
                                html += '<td id="url_' + crm_list[i][0] + '">' + crm_list[i][2] + "</td>";
                                // html += '<td id="id1_' + crm_list[i][0] + '">' + crm_list[i][3] + "</td>";
                                // html += '<td id="pass1_' + crm_list[i][0] + '">' + crm_list[i][4] + "</td>";
                                // html += '<td id="id2_' + crm_list[i][0] + '">' + crm_list[i][5] + "</td>";
                                // html += '<td id="pass2_' + crm_list[i][0] + '">' + crm_list[i][6] + "</td>";
                                html += '<td id="goal_' + crm_list[i][0] + '">' + crm_list[i][7] + "</td>";
                                if ("1" == crm_list[i][8]) {
                                    html += '<td id="paused_' + crm_list[i][0] + '"><span class="payment_badge payment_badge_red">Paused</span></td>';
                                }
                                else {
                                    html += '<td id="paused_' + crm_list[i][0] + '"></td>'
                                }
                                if ("0000-00-00" == crm_list[i][9] || null == crm_list[i][9]) {
                                    html += '<td id="valid_' + crm_list[i][0] + '"><span class="payment_badge payment_badge_red">No set password date</span></td>';
                                } else {
                                    var updated_date = crm_list[i][9].split("-");
                                    var cur_date = crm_list[i][10].split("-");

                                    var updated = Date.UTC(updated_date[0], updated_date[1] - 1, updated_date[2]);
                                    var cur = Date.UTC(cur_date[0], cur_date[1] - 1, cur_date[2]);

                                    var m = 30 - Math.abs((updated.valueOf() - cur.valueOf()) / 864e5);
                                    if (m < 0) {
                                        m = 0;
                                    }
                                    html += m < 5 ? '<td id="valid_' + crm_list[i][0] + '"><span class="payment_badge payment_badge_red">' + m + "</span></td>" : '<td id="valid_' + crm_list[i][0] + '">' + m + "</td>";
                                }
                                html += '<td id="rebill_' + crm_list[i][0] + '">' + crm_list[i][11] + "</td>";
                                // if (null == crm_list[j][12])
                                //     html += '<td id="test_' + crm_list[j][0] + '"></td>';
                                // else
                                //     html += '<td id="test_' + crm_list[j][0] + '">' + crm_list[j][12] + '</td>';
                                html += "<td>";
                                html += '<button type="button" class="btn btn-link btn-sm setting_crm_edit" id="' + crm_list[i][0] + '" data-toggle="modal" data-target="#crm_edit_modal"><span class="glyphicon glyphicon-edit" aria-hidden="true"></span>&nbsp;Edit</button>';
                                // html += '<button type="button" class="btn btn-link btn-sm setting_crm_password" id="' + crm_list[i][0] + '" data-toggle="modal" data-target="#crm_password_modal"><span class="glyphicon glyphicon-lock" aria-hidden="true"></span>&nbsp;CRM Password</button>';
                                // html += '<button type="button" class="btn btn-link btn-sm setting_api_password" id="' + crm_list[i][0] + '" data-toggle="modal" data-target="#api_password_modal"><span class="glyphicon glyphicon-lock" aria-hidden="true"></span>&nbsp;API Password</button>';
                                html += '<button type="button" class="btn btn-link btn-sm setting_crm_delete" id="' + crm_list[i][0] + '" data-toggle="modal" data-target="#crm_delete_modal"><span class="glyphicon glyphicon-minus-sign" aria-hidden="true" style="color: #ffa5a5"></span>&nbsp;Delete</button>';
                                html += "</td></tr>";
                            }
                        } else {
                            show_alert("main", "There is no any crm data.");
                        }
                        $(".table_crm_body").html(html);
                    }
                },
                failure : function() {
                    show_waiting(false);
                    show_alert("main", "Cannot load CRM list.");
                }
            });
        }
    }

    function setting_crm_add() {
        show_waiting(true);
        let pause_crm = 0;
        if ($(".add_crm_paused").prop("checked")) {
            pause_crm = 1;
        }
        $.ajax({
            type : "GET",
            url : "../daemon/ajax_admin/setting_crm_add.php",
            data : {
                crm_name : $(".add_crm_name").val(),
                crm_url : $(".add_crm_url").val(),
                crm_username : $(".add_crm_username").val(),
                crm_password : $(".add_crm_password").val(),
                api_username : $(".add_api_username").val(),
                api_password : $(".add_api_password").val(),
                sales_goal : $(".add_sales_goal").val(),
                rebill_length : $(".add_rebill_length").val(),
                test_cc : $(".add_test_cc").val(),
                crm_paused : pause_crm
            },
            success : function(data) {
                show_waiting(false);
                if ("error" == data) {
                    show_alert("main", "CRM cannot be added.");
                }
                else if ("no_cookie" == data) {
                    window.location.href = "../../admin/login.php";
                }
                else {
                    get_all_crm_list();
                }
            },
            failure : function() {
                show_waiting(false);
                show_alert("main", "CRM cannot be added.");
            }
        });
    }

    function setting_crm_edit() {
        show_waiting(true);
        let pause_crm = 0;
        if ($(".edit_crm_paused").prop("checked")) {
            pause_crm = 1;
        }
        $.ajax({
            type : "GET",
            url : "../daemon/ajax_admin/setting_crm_edit.php",
            data : {
                crm_id : crm_id,
                crm_name : $(".edit_crm_name").val(),
                crm_url : $(".edit_crm_url").val(),
                crm_username : $(".edit_crm_username").val(),
                crm_password : $(".edit_crm_password").val(),
                api_username : $(".edit_api_username").val(),
                api_password : $(".edit_api_password").val(),
                sales_goal : $(".edit_sales_goal").val(),
                rebill_length : $(".edit_rebill_length").val(),
                test_cc : $(".edit_test_cc").val(),
                crm_paused : pause_crm
            },
            success : function(data) {
                show_waiting(false);
                if ("error" == data) {
                    show_alert("main", "CRM information cannot be changed.");
                }
                else if ("no_cookie" == status) {
                    window.location.href = "../../admin/login.php";
                }
                else {
                    get_all_crm_list();
                }
            },
            failure : function() {
                show_waiting(false);
                show_alert("main", "CRM information cannot be changed.");
            }
        });
    }

    function setting_crm_crmpass() {
        show_waiting(true);
        $.ajax({
            type : "GET",
            url : "../daemon/ajax_admin/setting_crm_crmpass.php",
            data : {
                crm_id : crm_id,
                crm_password : $(".edit_crm_password").val()
            },
            success : function(data) {
                show_waiting(false);
                if ("success" == data) {
                    get_all_crm_list();
                }
                else if ("no_cookie" == data) {
                    window.location.href = "../../admin/login.php";
                }
                else {
                    show_alert("main", "CRM Password cannot be changed.");
                }
            },
            failure : function() {
                show_waiting(false);
                show_alert("main", "CRM Password cannot be changed.");
            }
        });
    }

    function setting_crm_apipass() {
        show_waiting(true);
        $.ajax({
            type : "GET",
            url : "../daemon/ajax_admin/setting_crm_apipass.php",
            data : {
                crm_id : crm_id,
                api_password : $(".edit_api_password").val()
            },
            success : function(data) {
                show_waiting(false);
                if ("success" == data) {
                    get_all_crm_list();
                }
                else if ("no_cookie" == data) {
                    window.location.href = "../../admin/login.php";
                }
                else {
                    show_alert("main", "API Password cannot be changed.");
                }
            },
            failure : function() {
                show_waiting(false);
                show_alert("main", "API Password cannot be changed.");
            }
        });
    }

    function setting_crm_delete() {
        show_waiting(true);
        $.ajax({
            type : "GET",
            url : "../daemon/ajax_admin/setting_crm_delete.php",
            data : {
                crm_id : crm_id
            },
            success : function(data) {
                show_waiting(false);
                if ("success" == data) {
                    get_all_crm_list();
                }
                else if ("no_cookie" == data) {
                    window.location.href = "../../admin/login.php";
                }
                else {
                    show_alert("main", "CRM cannot be deleted.");
                }
            },
            failure : function() {
                show_waiting(false);
                show_alert("main", "CRM cannot be deleted.");
            }
        });
    }

    let crm_id = -1;
    let crm_list = null;
    let is_waiting = false;
    let loading_icon = '<img src="../images/loading.gif" style="width:22px;height:22px;">';
    get_all_crm_list();

    $(".btn_crm_add").click(function() {
        $(".add_crm_name").val("");
        $(".add_crm_url").val("");
        $(".add_crm_username").val("");
        $(".add_crm_password").val("");
        $(".add_crm_repassword").val("");
        $(".add_api_username").val("");
        $(".add_api_password").val("");
        $(".add_api_repassword").val("");
        $(".add_sales_goal").val("");
        $(".add_crm_paused").prop("checked", false);
    });
    $(".modal_btn_crm_add").click(function() {
        if ("" == $(".add_crm_name").val()) {
            show_alert("edit", "Please input CRM Name.");
            $(".add_crm_name").focus();
            return;
        }
        else if ("" == $(".add_crm_url").val()) {
            show_alert("edit", "Please input CRM Site URL.");
            $(".add_crm_url").focus();
            return;
        }
        else if ("" == $(".add_crm_username").val()) {
            show_alert("edit", "Please input CRM User Name.");
            $(".add_crm_username").focus();
            return;
        }
        else if ("" == $(".add_crm_password").val()) {
            show_alert("edit", "Please input CRM Password.");
            $(".add_crm_password").focus();
            return;
        }
        else if ("" == $(".add_crm_repassword").val()) {
            show_alert("edit", "Please input CRM Password again.");
            $(".add_crm_repassword").focus();
            return;
        }
        else if ($(".add_crm_password").val() != $(".add_crm_repassword").val()) {
            show_alert("add", "Doesn't match CRM Password.");
            $(".add_crm_repassword").focus();
            return;
        }
        else if ("" == $(".add_api_username").val()) {
            show_alert("edit", "Please input API User Name.");
            $(".add_api_username").focus();
            return;
        }
        else if ("" == $(".add_api_password").val()) {
            show_alert("edit", "Please input API Password.");
            $(".add_api_password").focus();
            return;
        }
        else if ("" == $(".add_api_repassword").val()) {
            show_alert("edit", "Please input API Password again.");
            $(".add_api_repassword").focus();
            return;
        }
        else if ($(".add_api_password").val() != $(".add_api_repassword").val()) {
            show_alert("add", "Doesn't match API Password.");
            $(".add_api_repassword").focus();
        }
        else if ("" == $(".add_sales_goal").val()) {
            show_alert("edit", "Please input Sales Goal.");
            void $(".add_sales_goal").focus();
            return;
        }
        else if ("" == $(".add_rebill_length").val()) {
            show_alert("edit", "Please input Rebill Length.");
            void $(".add_rebill_length").focus();
            return;
        }
        else if ("" == $(".add_test_cc").val()) {
            show_alert("edit", "Please input Test CC.");
            void $(".add_test_cc").focus();
            return;
        }
        $("#crm_add_modal").modal("toggle");
        setting_crm_add();
    });
    $(".table_crm_body").on("click", ".setting_crm_edit", function() {
        crm_id = $(this).prop("id");
        let crm = crm_list.filter(item => item[0] == crm_id)[0];
        $(".edit_crm_name").val(crm[1]);
        $(".edit_crm_url").val(crm[2]);
        $(".edit_crm_username").val(crm[3]);
        $(".edit_crm_password").val(crm[4]);
        $(".edit_api_username").val(crm[5]);
        $(".edit_api_password").val(crm[6]);
        $(".edit_sales_goal").val(crm[7]);
        $(".edit_rebill_length").val(crm[11]);
        $(".edit_test_cc").val(crm[12]);
        if (1 == crm[8]) {
            $(".edit_crm_paused").prop("checked", true);
        } else {
            $(".edit_crm_paused").prop("checked", false);
        }
    });
    $(".modal_btn_crm_edit").click(function() {
        if ("" == $(".edit_crm_name").val()) {
            show_alert("edit", "Please input CRM Name.");
            $(".edit_crm_name").focus();
            return;
        }
        else if ("" == $(".edit_crm_url").val()) {
            show_alert("edit", "Please input CRM Site URL.");
            $(".edit_crm_url").focus();
            return;
        }
        else if ("" == $(".edit_crm_username").val()) {
            show_alert("edit", "Please input CRM User Name.");
            $(".edit_crm_username").focus();
            return;
        }
        else if ("" == $(".edit_crm_password").val()) {
            show_alert("edit", "Please input CRM Password.");
            $(".edit_crm_password").focus();
            return;
        }
        else if ("" == $(".edit_api_username").val()) {
            show_alert("edit", "Please input API User Name.");
            $(".edit_api_username").focus();
            return;
        }
        else if ("" == $(".edit_api_password").val()) {
            show_alert("edit", "Please input API Password.");
            $(".edit_api_password").focus();
            return;
        }
        else if ("" == $(".edit_sales_goal").val()) {
            show_alert("edit", "Please input Sales Goal.");
            void $(".edit_sales_goal").focus();
            return;
        }
        else if ("" == $(".edit_rebill_length").val()) {
            show_alert("edit", "Please input Rebill Length.");
            void $(".edit_rebill_length").focus();
            return;
        }
        else if ("" == $(".edit_test_cc").val()) {
            show_alert("edit", "Please input Test CC.");
            void $(".edit_test_cc").focus();
            return;
        }
        $("#crm_edit_modal").modal("toggle");
        setting_crm_edit();
    });
    $(".table_crm_body").on("click", ".setting_crm_password", function() {
        crm_id = $(this).prop("id");
        $(".edit_crm_password").val("");
        $(".edit_crm_repassword").val("");
    });
    $(".modal_btn_crm_password").click(function() {
        return "" == $(".edit_crm_password").val() ? (show_alert("crm_password", "Please input CRM Password."), void $(".edit_crm_password").focus()) : $(".edit_crm_password").val() != $(".edit_crm_repassword").val() ? (show_alert("crm_password", "Doesn't match CRM Password."), void $(".edit_crm_repassword").focus()) : ($("#crm_password_modal").modal("toggle"), void setting_crm_crmpass());
    });
    $(".table_crm_body").on("click", ".setting_api_password", function(canCreateDiscussions) {
        crm_id = $(this).prop("id");
        $(".edit_api_password").val("");
        $(".edit_api_repassword").val("");
    });
    $(".modal_btn_api_password").click(function() {
        return "" == $(".edit_api_password").val() ? (show_alert("api_password", "Please input API Password."), void $(".edit_api_password").focus()) : $(".edit_api_password").val() != $(".edit_api_repassword").val() ? (show_alert("api_password", "Doesn't match API Password."), void $(".edit_api_repassword").focus()) : ($("#api_password_modal").modal("toggle"), void setting_crm_apipass());
    });
    $(".table_crm_body").on("click", ".setting_crm_delete", function(canCreateDiscussions) {
        crm_id = $(this).prop("id");
    });
    $(".modal_btn_crm_delete").click(function() {
        $("#crm_delete_modal").modal("toggle");
        setting_crm_delete();
    });
});
