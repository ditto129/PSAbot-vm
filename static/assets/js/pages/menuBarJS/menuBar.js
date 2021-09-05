//var head_url = "http://127.0.0.1/";
var userPicSrc;
var session_id;
var first_start = true;
function changePage() {
    console.log("變更頁面");
    var page = localStorage.getItem("page");
    console.log(page);
    var content = "";
    content += '<iframe MARGINWIDTH=0 MARGINHEIGHT=0 HSPACE=0 VSPACE=0 frameborder=0 scrolling=auto src="';
    content += page;
    //    content += '.html';
    content += '" height="100%" width="100%"></iframe>';
    console.log("content: " + content);
    document.getElementById("main_page").innerHTML = content;
}

////////////////// 聊天室 START ////////////////////

var keyWords = {};
var needToClearBotMessage = false;
var preMessage = "";

function bot(string) {
    console.log("bot的回覆: "+string);
    //----- 設定preMessage START -----//
    if(string.slice(0,7)=="popover"){
        console.log("彈出選標籤的視窗");
        $("#discussTags").modal('show');
        preMessage = "";
    }
    //----- 設定preMessage END -----//
    
    keyWords = {};

    if (needToClearBotMessage) {
        //        console.log("有進來清");
        var obj = document.getElementById("willBeClear");
        obj.innerHTML = "";
        var objParent = obj.parentNode;
        objParent.removeChild(obj);
        needToClearBotMessage = false;
        //        console.log("object: ");
        //        console.log(obj);
    }

    var history = document.getElementById("history_message");
    var content = history.innerHTML;


    content += '<div ';
    if (string.slice(0, 6) == "正在輸入訊息") {
        needToClearBotMessage = true;
        content += 'id="willBeClear" ';
        //        console.log("下一次要清掉");
    }
    content += 'class="d-flex justify-content-start mb-4">';
    content += '<div class="img_cont_msg">';
    content += '<img src="../static/images/iconSmall.png" class="chatImg" style="background-color: #5D478B;">';
    content += '</div>';
    content += '<div class="msg_cotainer"';
    if (string.slice(0, 6) == "正在輸入訊息") {
        //        needToClearBotMessage = true;
        content += 'id="willBeClearString" ';
        //        console.log("下一次要清掉");
    }
    content += '>';
    content += string;

    //    content += '<span class="msg_time">8:40 AM</span>';
    content += '</div>';
    content += '</div>';

    history.innerHTML = content;
    history.scrollTop = history.scrollHeight;
    // 
    setInterval(function () {
        if (document.getElementById("willBeClearString") != null) {
            var botStringTemp = document.getElementById("willBeClearString").innerHTML;
            switch (botStringTemp) {
                case "正在輸入訊息...":
                    botStringTemp = "正在輸入訊息.";
                    break;
                case '正在輸入訊息.':
                    botStringTemp = "正在輸入訊息..";
                    break;
                case "正在輸入訊息..":
                    botStringTemp = "正在輸入訊息...";
                    break;
            }
            document.getElementById("willBeClearString").innerHTML = botStringTemp;
        }
    }, 1000);
    //

    // 處理關鍵字 START
    var temp = document.getElementById("keywords");
    if (temp != null) {
        var textArea = document.getElementById("message");
        textArea.setAttribute("placeholder", "請點選「新增」或「完成」");
        textArea.disabled = true;

        var sendBtn = document.getElementById("sendButton");
        sendBtn.disabled = true;

        var count = temp.getElementsByTagName("label").length;

        for (var i = 0; i < count; i++) {

            var tempName = document.getElementById(i).textContent;
            tempName = tempName.slice(0, -1);

            keyWords[i] = tempName;
        }
        console.log("keywords: ");
        console.log(keyWords);
    }
    // 處理關鍵字 END
}

function user(string) {
    //    console.log("user送訊息");
    var history = document.getElementById("history_message");
    var content = history.innerHTML;
    content += '<div class="d-flex justify-content-end mb-4">';
    content += '<div class="msg_cotainer_send">';
    content += string;
    //    content += '<span class="msg_time">8:40 AM</span>';
    content += '</div>';
    content += '<div class="img_cont_msg">';
    content += '<img src="';
    content += userPicSrc;
    content += '" class="chatImg">';
    content += '</div>';
    content += '</div>';

    history.innerHTML = content;
    history.scrollTop = history.scrollHeight;

    bot("正在輸入訊息...");
}

function send_message() {
    console.log("send_message");
    var message = $("#message").val();
    console.log("message: " + message);

    user(message);
    // 共同討論有些要加上前綴
    message = preMessage + message;
    
    //用來清空傳出去的輸入框
    var msg = document.getElementById("message");
    msg.value = "";
    
    //直接用session_id會undifine!!
    session_id = localStorage.getItem("sessionID");
    var myURL = head_url + "base_flow_rasa?message=" + message + "&sender_id=" + session_id;
    myURL = encodeURI(myURL);
    console.log("送出訊息: "+myURL);
    $.ajax({
        url: myURL,
        type: "GET",
        dataType: "json",
        contentType: 'application/json; charset=utf-8',
        success: function (response) {
            console.log("收到的response: ");
            console.log(response);
            bot(response.text);
            //----- 設定preMessage START -----//
            // 要確保訊息已經送出去，才能加前綴
            if(message=="共同討論"){
                preMessage = "discuss_together_whether_incognito,";
            }
            //----- 設定preMessage END -----//
        },
        error: function () {
            console.log("error");
        }
    });
}

// 關鍵字們 START
function wantAddKeyWord() {

    var textArea = document.getElementById("message");
    textArea.disabled = false;
    textArea.setAttribute("placeholder", "請輸入欲新增之關鍵字");

    var sendBtn = document.getElementById("sendButton");
    sendBtn.disabled = false;
    sendBtn.setAttribute("onclick", "addKeyWord()");
}

function addKeyWord() {
    var max = -1;
    for (var temp in keyWords) {
        if (parseInt(temp) > max) {
            max = parseInt(temp);
        }
    }
    max += 1;

    var newKeyWord = $("#message").val();
    var msg = document.getElementById("message");
    msg.value = "";

    var keyWordsArea = document.getElementById("keywords");
    keyWords[max] = newKeyWord;
    showKeyWords();

    var textArea = document.getElementById("message");
    textArea.setAttribute("placeholder", "請點選「新增」或「完成」");
    textArea.disabled = true;

    var sendBtn = document.getElementById("sendButton");
    sendBtn.disabled = true;
}

function showKeyWords() {
    var content = "";
    for (var id in keyWords) {
        content += '<label id="';
        content += id;
        content += '" class="badge badge-default purpleLabel">';
        content += keyWords[id];
        content += '<button class="labelXBtn" onclick="cancleKeyWords(';
        content += "'";
        content += id;
        content += "'";
        content += ')">x</button></label>';
    }
    document.getElementById("keywords").innerHTML = content;
}

function cancleKeyWords(keyWordId) {
    //    console.log("取消前: ");
    //    console.log(keyWords);
    delete keyWords[keyWordId];
    showKeyWords();
    //    console.log("取消後: ");
    //    console.log(keyWords);
}

var postNumber;
function doneKeyWord() {

    // 恢復原廠設定 START
    var textArea = document.getElementById("message");
    textArea.setAttribute("placeholder", "輸入...");
    textArea.disabled = false;

    var sendBtn = document.getElementById("sendButton");
    sendBtn.disabled = false;
    sendBtn.setAttribute("onclick", "send_message()");
    // 恢復原廠設定 END

    document.getElementById("addBtn").setAttribute("style", "background-color: gray; border-color: gray;");
    document.getElementById("doneBtn").setAttribute("style", "background-color: gray; border-color: gray;");
    document.getElementById("addBtn").disabled = true;
    document.getElementById("doneBtn").disabled = true;

    document.getElementById("addBtn").removeAttribute("id");
    document.getElementById("doneBtn").removeAttribute("id");


    var sendKeyWords = "keywords";
    for (var id in keyWords) {
        sendKeyWords += ",";
        sendKeyWords += keyWords[id];
        document.getElementById(id).setAttribute("style", "background-color: gray;");
        document.getElementById(id).removeAttribute("id");
    }
    var keyWordsBtn = document.getElementById("keywords").getElementsByTagName("button");
    for (var i = 0; i < keyWordsBtn.length; i++) {
        keyWordsBtn[i].disabled = true;
    }
    console.log("keyWordsBtn");
    console.log(keyWordsBtn);

    document.getElementById("keywords").removeAttribute("id");

    console.log("送出字串: " + sendKeyWords);

    var content = "";
    postNumber = 1;
    // outerSearch START
    // 傳給rasa START
    var sessionId = localStorage.getItem("sessionID");
    var myURL = head_url + "keywords?sender_id=" + sessionId + "&keywords=" + sendKeyWords;
    console.log("myURL: " + myURL);
    $.ajax({
        url: myURL,
        type: "GET",
        dataType: "json",
        async: false,
        contentType: 'application/json; charset=utf-8',
        success: function (response) {
            console.log("outerSearch");
            console.log("response: ");
            console.log(response);
        },
        error: function () {
            console.log("error");
        }
    });
    // 傳給rasa END
    // outerSearch END

    //innerSearch START
    var myURL = head_url + "query_inner_search";
    console.log("myURL: " + myURL);
    var tempKeywords = []
    for (var id in keyWords) {
        sendKeyWords += ",";
        tempKeywords.push(keyWords[id]);
    }
    var data = { keywords: tempKeywords };
    console.log(data);

    var myURL = head_url + "query_inner_search";
    $.ajax({
        url: myURL,
        type: "POST",
        data: JSON.stringify(data),
        async: false,
        dataType: "json",
        contentType: 'application/json; charset=utf-8',
        success: function (response) {
            console.log("成功: 內部貼文搜尋（query_inner_search）");
            console.log(response);
            content = innerSearch(response, content);
        },
        error: function (response) {
            console.log("失敗: 內部貼文搜尋（query_inner_search）");
            console.log(response);
        }
    });
    //innerSearch END
    bot(content);
}
// 關鍵字們 END

// innerSearch START
function innerSearch(response, content) {
    for (var i = 0; i < response.inner_search_result.length; i++) {
        var data = { _id: response.inner_search_result[i] };
        console.log(data);

        var myURL = head_url + "query_inner_post";
        $.ajax({
            url: myURL,
            type: "POST",
            data: JSON.stringify(data),
            async: false,
            dataType: "json",
            contentType: 'application/json; charset=utf-8',
            success: function (response) {
                console.log("成功: 內部貼文（query_inner_post）");
                console.log(response);
                content += postNumber;
                content += '. <a href="#" onclick="clickChatroomInnerSearch(\'';
                content += response._id;
                content += '\')">';
                content += response.title;
                content += '</a><br>';
                postNumber += 1;
            },
            error: function (response) {
                console.log("失敗: 內部貼文（query_inner_post）");
                console.log(response);
            }
        });
    }
    return content;
}

function clickChatroomInnerSearch(postId) {
    localStorage.setItem("postType", "innerPost");
    localStorage.setItem("singlePostId", postId);
    setPage('mySinglePostFrame');
}
// innerSearch END

// outerSearch START
function summary(id) {//單篇的摘要
    console.log("單篇的摘要");
    console.log("id: " + id);
    localStorage.setItem("summaryId", id);
    console.log("拿到的: " + localStorage.getItem("summaryId"));
    setPage('summary_new');
}

function rank(id) {//全部的排行
    //    var idArray = ['t_000001', 't_000002', 't_000003', 't_000004', 't_000005'];
    localStorage.setItem("rankId", id);
    setPage('comprehensive');
}
// outerSearch END

////////////////// 聊天室 END ////////////////////

////////////////// 初始化 START////////////////////
function start() {
    //如果是第一次登入，要先跳出編輯個人資訊的頁面 START
    var role = localStorage.getItem("role");
    var first = localStorage.getItem("first_login");
    if (role != "manager" && first == "true") {
        $("#exampleModal").modal('show');
    }
    localStorage.removeItem("first_login");
    //如果是第一次登入，要先跳出編輯個人資訊的頁面 END
    //這個是管理者
    //    localStorage.setItem("role", "manager");
    //    localStorage.setItem("sessionID", 4444);

    // 這個是一般使用者
    //    localStorage.setItem("role", "generalUser");
    //    localStorage.setItem("sessionID", 123);
    var session_id = localStorage.getItem("sessionID");

    // ---------- 同個頁面監聽localStorage START ---------- //
    var orignalSetItem = localStorage.setItem;

    localStorage.setItem = function (key, newValue) {
        orignalSetItem.apply(this, arguments);
        var setItemEvent = new Event("setItemEvent");
        setItemEvent.newValue = newValue;
        window.dispatchEvent(setItemEvent);
    }
    window.addEventListener("setItemEvent", function (e) {
        changePage();
    });
    // ---------- 同個頁面監聽localStorage END ---------- //

    localStorage.setItem("page", "home");

    $(document).ready(function () {
        $('#action_menu_btn').click(function () {
            $('.action_menu').toggle();
        });
    });
    
    setMenuBar();
    if(session_id!=undefined){
        // ---------- 個人資料 START ---------- //
        showIdentity();
        getUserHeadshotAndName();
        var role = localStorage.getItem("role");
        if (role == "facebook_user" || role == "google_user") {
            getUserInterestTags();
        }
        // ---------- 個人資料 END ---------- //

        var role = localStorage.getItem("role");
        if (role != "manager") {
            // ---------- PSABot聊天室 START ---------- //
            //到時候要用session_id

            //傳session_start
            var myURL = head_url + "session_start?sender_id=" + session_id;
            console.log("myURL: " + myURL);
            $.ajax({
                url: myURL,
                type: "GET",
                dataType: "json",
                async: false,
                contentType: 'application/json; charset=utf-8',
                success: function (response) {
                    console.log("response: " + response);
                    console.log(response);
                },
                error: function () {
                    console.log("error");
                }
            });


            var myURL = head_url + "welcome?sender_id=" + session_id;
            console.log("myURL: " + myURL);
            $.ajax({
                url: myURL,
                type: "GET",
                dataType: "json",
                async: false,
                contentType: 'application/json; charset=utf-8',
                success: function (response) {
                    console.log("");
                    console.log(response);
                    bot(response.text)
                },
                error: function () {
                    console.log("error");
                }
            });
            // ---------- PSABot聊天室 END ---------- //
        }   
    }

}

function setMenuBar() {
    var role = localStorage.getItem("role"), start, end;
    var leftManuBarPagesContent = "";
    var setPage = ["home", "profileFrame", "postQuestionFrame", "postRowFrame", "FaqFrame", "home", "postRowFrame", "FaqFrame", "manageDataFrame", "home", "postRowFrame", "FaqFrame"];
    var pageIcon = ["ti-home", "fa fa-user-o", "fa fa-file-text-o", "fa fa-eye", "fa fa-cogs", "ti-home", "fa fa-clipboard", "fa fa-cogs", "fa fa-wrench", "ti-home", "fa fa-eye", "fa fa-cogs"];
    var pageName = ["首頁", "個人頁面", "發布貼文", "瀏覽貼文", "瀏覽FAQ", "首頁", "管理內部貼文", "管理FAQ資料", "管理資料更新數據", "首頁", "瀏覽貼文", "瀏覽FAQ"];

    if (role == "facebook_user" || role == "google_user") {
        start = 0;
        end = 5;
    }
    else if (role == "manager") {
        start = 5;
        end = 9;
        document.getElementById("interestingTags").innerHTML = "";
    }
    else{
        start = 9;
        end = 12;
        document.getElementById("interestingTags").innerHTML = "";
    }

    for (var i = start; i < end; i++) {
        leftManuBarPagesContent += '<li>';
        leftManuBarPagesContent += '<a href="#" onclick="setPage(\'';
        leftManuBarPagesContent += setPage[i];
        leftManuBarPagesContent += '\')">';
        leftManuBarPagesContent += '<span class="pcoded-micon"><i class="';
        leftManuBarPagesContent += pageIcon[i];
        leftManuBarPagesContent += '" aria-hidden="true"></i></span>';
        leftManuBarPagesContent += '<span class="pcoded-mtext" data-i18n="nav.dash.main">';
        leftManuBarPagesContent += pageName[i];
        leftManuBarPagesContent += '</span>';
        leftManuBarPagesContent += '<span class="pcoded-mcaret"></span>';
        leftManuBarPagesContent += '</a>';
        leftManuBarPagesContent += '</li>';
    }

    // 登出Button
    leftManuBarPagesContent += '<li style="position: fixed; bottom: 10px; display: block;">';
    if(role==undefined){
       leftManuBarPagesContent += '<a href="#" onclick="returnToLogin()">';
    }
    else{
       leftManuBarPagesContent += '<a href="#" onclick="logOut()">';
    }
    leftManuBarPagesContent += '<button class="btn btn-outline" style="width: 230px; background-color: #5D478B;">';
    leftManuBarPagesContent += '<i class="fa fa-sign-out" aria-hidden="true" style="color: white;"></i>';
    if(role==undefined){
        leftManuBarPagesContent += '<span data-i18n="nav.dash.main" style="color: white;">登入</span>';
    }
    else{
        leftManuBarPagesContent += '<span data-i18n="nav.dash.main" style="color: white;">登出</span>';
    }
    leftManuBarPagesContent += '</button>';
    leftManuBarPagesContent += '</a>';
    leftManuBarPagesContent += '</li>';


    document.getElementById("leftMenuBarPages").innerHTML = leftManuBarPagesContent;
}

////////////////// 初始化 END////////////////////

function getUserInterestTags() {
    language = [];
    children = [];
    originTags = [];
    chosenTags = [];

    // 取得興趣標籤 START
    var sessionId = localStorage.getItem("sessionID");
    var data = { _id: sessionId };

    myURL = head_url + "query_user_skill";
    $.ajax({
        url: myURL,
        type: "POST",
        data: JSON.stringify(data),
        async: false,
        dataType: "json",
        contentType: 'application/json; charset=utf-8',
        success: function (response) {
            console.log("成功: 興趣標籤（query_user_skill）");
            console.log(response);

            for (var i = 0; i < response.length; i++) {
                if (response[i].interested_score == 1) {
                    originTags.push(response[i].tag_id);
                    chosenTags.push(response[i].tag_id);
                }
            }
        },
        error: function (response) {
            console.log("失敗: 興趣標籤（query_user_skill）");
            console.log(response);
        }
    });
    // 取得興趣標籤 END

    getLanguageTag();
    showChosenTags();
}

function open_close() {
    if ($("#chatroom").is(':visible')) {

        $("#chatroom").addClass("animate__backOutRight");

        $("#chatroom").toggle(function () {
            window.setTimeout(function () {
                $("#chatroom").removeClass("animate__backOutRight")
            }, 1500);
        });

    } else {
        $("#chatroom").addClass("animate__backInRight");

        $("#chatroom").toggle(function () {
            window.setTimeout(function () {
                $("#chatroom").removeClass("animate__backInRight")
            }, 1500);
        });
    }

}

//編輯個人資訊 START

//////////////////照片＆姓名 START////////////////////

function showIdentity() {
    var role = localStorage.getItem("role");
    if (role == "facebook_user" || role == "google_user") {
        document.getElementById("userRoleMenubar").innerHTML = "一般使用者";
    }
    else if (role == "manager") {
        document.getElementById("userRoleMenubar").innerHTML = "管理者";
    }
    else {
        document.getElementById("userRoleMenubar").innerHTML = "未知";
    }
}

var userHeadshotURL = "";

$("#headshotBtn").change(function () {
    readURL(this);
});

function readURL(input) {
    var reader;
    if (input.files && input.files[0]) {
        reader = new FileReader();
        reader.onload = function (e) {
            $("#headshot").attr("src", e.target.result);
            userHeadshotURL = e.target.result;
        }
        reader.readAsDataURL(input.files[0]);
    }
}

// 抓新資料顯示在menuBar上
// 同時更新modal的內容
function getUserHeadshotAndName() {

    // 照片
    var id = localStorage.getItem("sessionID");
    var myURL = head_url + "read_image?user_id=" + id;
    var img = "";
    $.ajax({
        url: myURL,
        type: "GET",
        dataType: "json",
        async: false,
        contentType: 'application/json; charset=utf-8',
        success: function (response) {
            console.log("成功: 拿照片（read_image）");
            img += '<img class="img-40 img-radius" alt="User-Profile-Image" src="';
            userPicSrc = response.src;
            img += response.src;
            img += '">';
            document.getElementById("headshot").setAttribute("src", response.src);
        },
        error: function (response) {
            console.log("失敗: 拿照片（read_image）");
        }
    });

    // 姓名
    myURL = head_url + "query_user_profile";

    var data = { "_id": id };
    var name = "";
    $.ajax({
        url: myURL,
        type: "POST",
        data: JSON.stringify(data),
        async: false,
        dataType: "json",
        contentType: 'application/json; charset=utf-8',
        success: function (response) {
            //            console.log("成功: 拿姓名（query_user_profile）");
            name += '<span>';
            name += response.name;
            name += '</span>';

            document.getElementById("userName").setAttribute("value", response.name);
            localStorage.setItem("userName", response.name);
        },
        error: function () {
            console.log("失敗: 拿姓名（query_user_profile）");
        }
    });

    document.getElementById("userHeadshotMenubar").innerHTML = img;
    document.getElementById("userNameMenubar").innerHTML = name;
    document.getElementById("userProfileNav").innerHTML = img + name;
}

//////////////////照片＆姓名 END//////////////////////


// 興趣標籤 START
// 用來記使用者選擇的所有標籤
var language = [];
var children = [];
var chosenTags = [];
var originTags = []; // 紀錄原本的使用者的tag有哪些
// 以上4個都是放id
var allTags = {};


//根據chosenTags的內容 顯示已選擇的tags
function showChosenTags(page) {
    var chosen_tag_content = "<hr>";

    for (var i = 0; i < chosenTags.length; i++) {
        chosen_tag_content += '<label class="badge purpleLabel" style="margin-right: 5px;">';
        chosen_tag_content += allTags[chosenTags[i]];

        chosen_tag_content += '<button type="button" class="labelXBtn" onclick="cancle(';
        chosen_tag_content += "'";
        chosen_tag_content += chosenTags[i];
        chosen_tag_content += "','";
        chosen_tag_content += page;
        chosen_tag_content += "'";
        chosen_tag_content += ')">x</button></label>';
    }

    document.getElementById("chosen_tag_in_modal").innerHTML = chosen_tag_content;
}

// 顯示可選擇的語言「子」標籤
function click_tag(id, page) {
    // tag -> 是選擇了哪個tag
    // page -> 是選語言(0) 還是選孩子(1)
    var tag = allTags[id];


    // 已選擇的tag START

    // card的最下面顯示已選擇的tags
    if (!chosenTags.includes(id)) { //如果還沒選過
        chosenTags.push(id);
        document.getElementById(id).setAttribute("style", "margin-right: 5px; background-color: #E6E6FA;");
        if (language.indexOf(id) == -1) {
            showChosenTags(1);
            console.log("page1");
        }
        else {
            showChosenTags(0);
            console.log("page0");
        }
    }
    // 已選擇的tag END


    // 可以選擇的標籤 START
    if (page == 0) {

        var myURL = head_url + "query_all_offspring_tag?tag_id=" + id;
        children = [];
        $.ajax({
            url: myURL,
            type: "GET",
            async: false,
            dataType: "json",
            contentType: 'application/json; charset=utf-8',
            success: function (response) {
                console.log("success");
                //先記下allTags 包含名字&ID
                for (var i = 0; i < response.tags.length; i++) {
                    console.log("i: " + i);

                    var temp = response.tags[i].tag_name;
                    temp = temp.replace("'", "&apos;");

                    children.push(response.tags[i].tag_id);
                }
            },
            error: function () {
                console.log("error");
            }
        });
        showChildrenAndSetColor();
    }
    // 可以選擇的標籤 END
}

function showChildrenAndSetColor() {
    localStorage.setItem("chooseTags", 1);

    // 標題 START
    // 需加上上一頁的按鈕
    var titleContent = "";
    titleContent += '<i class="fa fa-angle-left scoreBtn" aria-hidden="true" onclick="showLanguageTag()" style="color: gray; margin-right: 5px;"></i>';
    titleContent += "上一頁";

    document.getElementById("forwardPage").innerHTML = titleContent;
    // 標題 END

    var content = "";
    for (var i = 0; i < children.length; i++) {
        content += '<label id="';
        content += children[i]; //這裡要放id
        content += '" class="badge purpleLabel2" style="margin-right: 5px;';
        if (chosenTags.indexOf(children[i]) != -1) {
            content += 'background-color: #E6E6FA;';
        }
        content += '" onclick="click_tag(';
        content += "'";
        content += children[i];
        content += "', '1'";
        content += ')">';
        content += allTags[children[i]];
        content += "</label>";
    }

    //    console.log("innerHTML: "+content);
    document.getElementById("chose_tag").innerHTML = content;
}

// 顯示可選擇的語言標籤
function getLanguageTag() {

    // 中間內容 START
    // 先去跟後端拿 只有顯示語言的標籤有哪些
    var myURL = head_url + "query_all_languages";
    $.ajax({
        url: myURL,
        type: "GET",
        dataType: "json",
        async: false,
        contentType: 'application/json; charset=utf-8',
        success: function (response) {
            console.log("success");
            //先記下allTags 包含名字&ID
            for (var i = 0; i < response.tags.length; i++) {
                language.push(response.tags[0]._id);
                allTags[response.tags[0]._id] = response.tags[0].tag;


                // 把allTags建好 START
                var tempURL = head_url + "query_all_offspring_tag?tag_id=" + response.tags[0]._id;

                $.ajax({
                    url: tempURL,
                    type: "GET",
                    async: false,
                    dataType: "json",
                    contentType: 'application/json; charset=utf-8',
                    success: function (response) {
                        console.log("success");
                        //先記下allTags 包含名字&ID
                        for (var i = 0; i < response.tags.length; i++) {

                            var temp = response.tags[i].tag_name;
                            temp = temp.replace("'", "&apos;");

                            allTags[response.tags[i].tag_id] = temp;
                        }
                    },
                    error: function () {
                        console.log("error");
                    }
                });
                // 把allTags建好 END
            }
            showLanguageTag();
        },
        error: function () {
            console.log("error");
        }
    });
    // 中間內容 END

    console.log("allTags: ");
    console.log(allTags);
}

// 顯示「語言」tag的content
function showLanguageTag() {
    // 不會有上一頁的按鈕 START
    var titleContent = "";
    document.getElementById("forwardPage").innerHTML = titleContent;
    // 不會有上一頁的按鈕 END

    localStorage.setItem("chooseTags", 0);
    var content = "";
    for (var i = 0; i < language.length; i++) {
        //        console.log("language.length: "+language.length);
        //        console.log("language[i]: "+language[i]);
        content += '<label id="';
        content += language[i];
        content += '" class="badge purpleLabel2" style="margin-right: 5px;';
        //如果選過要變色
        if (chosenTags.indexOf(language[i]) != -1) {
            content += 'background-color: #E6E6FA;';
        }
        content += '" onclick="click_tag(';
        content += "'";
        content += language[i];
        content += "', '0'"
        content += ')">';
        content += allTags[language[i]];
        content += '</label>';
    }

    document.getElementById("chose_tag").innerHTML = content;
}

// 取消選擇tag後的處理
function cancle(id, page) {

    var index = chosenTags.indexOf(id);
    if (index != -1) {
        chosenTags.splice(index, 1);
        showChosenTags(page);
    }

    var temp = parseInt(localStorage.getItem("chooseTags"));
    console.log("page為: " + temp);
    if (temp == 0 && language.indexOf(id) == -1) {
        showChildrenAndSetColor();
        showLanguageTag();
        localStorage.setItem("chooseTags", 0);
    }
    else if (temp == 0 && language.indexOf(id) != -1) {
        showLanguageTag();
    }
    else if (temp == 1 && language.indexOf(id) == -1) {
        showChildrenAndSetColor();
    }
    else {
        showLanguageTag();
        showChildrenAndSetColor();
        localStorage.setItem("chooseTags", 1);
    }
}
// 興趣標籤 END


//////////////////儲存 照片＆姓名＆興趣標籤 START////////////////////
function save() {
    // 把資料傳給後端
    var name = $("#userName").val();
    if(name.length==0){
       $("#warning").modal('show');
    }
    else{
        var userId = localStorage.getItem("sessionID");
        var userImgName = userId + ".png";
        let form = new FormData();
        if (document.getElementById("headshotBtn").files[0] != null) {
            form.append("img", document.getElementById("headshotBtn").files[0], userImgName);

            var myURL = head_url + "save_user_img";

            fetch(myURL, {
                method: 'POST',
                body: form,
                async: false,
            }).then(res => {
                return res.json();   // 使用 json() 可以得到 json 物件
            }).then(result => {
                console.log(result); // 得到 {name: "oxxo", age: 18, text: "你的名字是 oxxo，年紀 18 歲～"}
            });
        }

        myURL = head_url + "update_user_profile";

        var data = { "_id": userId, "name": name };
        console.log("給後端的: ");
        console.log(data);
        $.ajax({
            url: myURL,
            type: "POST",
            data: JSON.stringify(data),
            async: false,
            dataType: "json",
            contentType: 'application/json; charset=utf-8',
            success: function (response) {
                console.log("收到的: ");
                console.log(response);
                localStorage.setItem("userName", name);
                //            console.log("成功: 更新姓名（update_user_profile）");
            },
            error: function (response) {
                console.log("失敗: 更新姓名（update_user_profile）");
                console.log(response);
            }
        });

        // 更新畫面
        getUserHeadshotAndName();

        // ---------- 傳興趣標籤 START ---------- //
        var sendTags = [];

        // 先檢查被取消的
        for (var i = 0; i < originTags.length; i++) {
            if (chosenTags.indexOf(originTags[i]) == -1) {
                var temp = { tag_id: originTags[i], skill_name: allTags[originTags[i]], interested_score: 0 };
                sendTags.push(temp);
            }
        }

        // 再新增要加上去的
        for (var i = 0; i < chosenTags.length; i++) {
            if (originTags.indexOf(chosenTags[i]) == -1) {
                var temp = { tag_id: chosenTags[i], skill_name: allTags[chosenTags[i]], interested_score: 1 };
                sendTags.push(temp);
            }
        }

        var data = { _id: userId, tag: sendTags }
        console.log("興趣標籤的修改: ");
        console.log(data);

        var myURL = head_url + "update_user_interest";
        $.ajax({
            url: myURL,
            type: "POST",
            data: JSON.stringify(data),
            async: false,
            dataType: "json",
            contentType: 'application/json; charset=utf-8',
            success: function (response) {
                console.log("成功: 修改興趣標籤（update_inner_post）");
                console.log(response);
            },
            error: function (response) {
                console.log("失敗: 修改興趣標籤（update_inner_post）");
                console.log(response);
            }
        });
        // ---------- 傳興趣標籤 END ---------- //

        getUserInterestTags();
    }

}
//////////////////儲存 照片＆姓名＆興趣標籤 END////////////////////

//編輯個人資訊 END

//////////// Google 登出需要 init gapi ////////////
window.onload = function(){
    gapi.load('auth2', function () {
        // Retrieve the singleton for the GoogleAuth library and set up the client.
        gapi.auth2.init({
            client_id: '417777300686-b6isl0oe0orcju7p5u0cpdeo07hja9qs.apps.googleusercontent.com',
            cookiepolicy: 'none',
            scope: 'profile'
        }).then(function (){
            console.log('gapi.auth2.init')
        });
    });
}
////////////////// 登出 START ////////////////////
function logOut() {
    if (localStorage.getItem('role') == 'google_user') {
        gapi.auth2.getAuthInstance().signOut().then(function () {
            console.log('Google User signed out.');
        });
    }
    else if (localStorage.getItem('role') == 'facebook_user') {
        FB.logout(function (response) {
            console.log('Facebook User logout.');
        });
    }
    // flask logout
    $.ajax({
        type: 'GET',
        url: head_url + 'logout',
        success: function () {
            console.log('flask logout.')
        }
    });
    localStorage.clear();
    window.location.href = "https://soselab.asuscomm.com:55002/site/login";
}

function returnToLogin(){
    localStorage.clear();
    window.location.href = "https://soselab.asuscomm.com:55002/site/login";
}
////////////////// 登出 END ////////////////////

////////////////// 不同頁面監聽localStorage START //////////////////
window.addEventListener("storage", function (e) {
    if (e.key == "page") {//判斷page是否改變
        console.log("page有改變");
        changePage();
    }
    else {
        console.log("是其他的有變～" + e.key);
    }
});
////////////////// 不同頁面監聽localStorage END ////////////////////

////////////////// 處理通知 START //////////////////
var notificationPage;
var notificationIndex = [];
var notificationEnd = false;

function setNotification() {
    // 開始監聽是否有新通知
    listenNotification();

    // 點擊小鈴鐺（要call API）
    var bell = document.getElementById("bell");
    bell.addEventListener("click", function () {
        notNewAnymore();
    }, false);
    bell.addEventListener("mouseover", function () {
        notNewAnymore();
    }, false);
    var showNotificationScope = document.getElementById("showNotification");
    showNotificationScope.addEventListener("mouseleave", function () {
        showNotificationScope.scrollTop = 0;
    }, false);

    // 初始化（先抓5筆資料）
    notificationPage = 0;
    notificationEnd = false;
    getNotification();

    // 開始監聽是否有滑動
    var showNotificationScope = document.getElementById("showNotification");
    showNotificationScope.addEventListener("scroll", moreNotification, false);
}

// 監聽是否有新通知（60秒一次）
function listenNotification() {
    if (localStorage.getItem("role") != "manager") {
        // 每5秒去檢查一次
        setInterval(function () {
            var myURL = head_url + "check_new_notification?user_id=" + localStorage.getItem("sessionID");
            $.ajax({
                url: myURL,
                type: "GET",
                async: false,
                dataType: "json",
                contentType: 'application/json; charset=utf-8',
                success: function (response) {
                    if (response.new == true) {
                        $("#newNotification").addClass("badge bg-c-pink");
                        notificationPage = 0;
                        getNotification();
                    }
                },
                error: function () {
                }
            });
        }, 60000);
    }
}

// 滑到底之後載入更多通知
function moreNotification() {
    var showNotificationScope = document.getElementById("showNotification");
    //    console.log("可視高度: "+showNotificationScope.clientHeight);
    //    console.log("總高度: "+showNotificationScope.scrollHeight);
    //    console.log("捲進去的高度: "+showNotificationScope.scrollTop);
    if (showNotificationScope.scrollTop + showNotificationScope.clientHeight >= showNotificationScope.scrollHeight) {
        if (notificationEnd == false) {
            notificationPage += 1;
            getNotification();
        }
    }
}

// 顯示通知
function showNotification(response) {
    console.log("收到的通知: ");
    console.log(response);
    notificationIndex = [];
    var content;
    if (notificationPage == 0) {
        content = "<li><h6>通知</h6></li>";
    }
    else {
        content = document.getElementById("showNotification").innerHTML;
    }
    if (response.result.length == 0) {
        if (notificationEnd == false && notificationPage == 0) {// 如果是第一次抓就沒資料，才要顯示
            content += '<li><div class="media"><div class="media-body">目前尚無通知</div></div></li>';
        }
        else {// 如果是滑到底以後沒資料 顯示「已經沒有更多通知了～」
            content += '<li><div class="media"><div class="media-body">已經沒有更多通知了～</div></div></li>';
        }
        notificationEnd = true;
    }
    for (var i = 0; i < response.result.length; i++) {
        notificationIndex.push(response.result[i].id);

        var now = new Date();
        var time = new Date(dateToJsType(response.result[i].time));
        var diff = new Date(Date.parse(now) - Date.parse(time));//相差幾毫秒

        if (diff < 86400000) { //同一天，一天有86400000毫秒
            if (diff < 3600000) { //幾分鐘前
                time = Math.floor(diff / 60000);
                time = time + "分鐘前";
                console.log(time);
            }
            else { //幾小時前
                time = Math.floor(diff / 3600000);
                time = time + "小時前";
                console.log(time);
            }
        }
        else { //不同天
            time = time.toISOString();
            time = time.slice(0, 10);
        }

        content += '<li id="background';
        content += response.result[i].id;
        content += '" style="background: ';
        // 是否看過 START
        if (response.result[i].check == false) {
            //            content += '<label id="notification';
            //            content += response.result[i].id;
            //            content += '" class="label label-danger align-self-center">是新的</label>';
            content += '#E6E6FA;">';
        }
        else {
            //            content += '<label id="notification';
            //            content += response.result[i].id;
            //            content += '" class="label label-danger align-self-center" style="background: #505458;">已看過</label>';
            content += '#FFFFFF;">';
        }
        // 是否看過 END

        content += '<div class="media" onclick="checkNotification(\'';
        content += response.result[i].detail.post_id;
        content += '\', \'';
        content += response.result[i].id;
        content += '\')">';

        // 拿照片 STRAT
        //                content += '<img class="d-flex align-self-center" src="../static/images/person_4.jpg" alt="Generic placeholder image">';
        content += '<i class="d-flex align-self-center fa-lg fa fa-reply-all" aria-hidden="true" style="margin: 10px;"></i>';
        //                content += '<i class="d-flex align-self-center fa-lg fa fa-comments-o" aria-hidden="true" style="margin: 10px;"></i>';
        // 拿照片 END

        content += '<div class="media-body">';
        //                    content += '<h5 class="notification-user">';
        //                        content += response.result[i].detail.replier_name;
        //                    content += '</h5>';
        content += '<p class="notification-msg">';
        content += response.result[i].detail.replier_name;
        content += '回覆了您的貼文</p>';
        content += '<span class="notification-time">';
        content += time;
        content += '</span>';
        content += '</div>';
        content += '</div>';
        content += '</li>';
    }
    document.getElementById("showNotification").innerHTML = content;
}

// 拿通知
function getNotification() {
    var myURL = head_url + "check_notification_content?user_id=" + localStorage.getItem("sessionID") + "&page=" + notificationPage;
    $.ajax({
        url: myURL,
        type: "GET",
        async: false,
        dataType: "json",
        contentType: 'application/json; charset=utf-8',
        success: function (response) {
            //            console.log("通知列表: ");
            //            console.log(response);
            showNotification(response);
        },
        error: function () {
            //            console.log("error");
        }
    });
}

// call API，代表通知已經不是新的了～
function notNewAnymore() {
    $("#newNotification").removeClass("badge bg-c-pink");
    var myURL = head_url + "set_notification_new";
    var data = { user_id: localStorage.getItem("sessionID"), id: notificationIndex };
    console.log("data: ");
    console.log(data);
    $.ajax({
        url: myURL,
        type: "POST",
        data: JSON.stringify(data),
        async: false,
        dataType: "json",
        contentType: 'application/json; charset=utf-8',
        success: function (response) {
            console.log("成功set_notification_new");
            console.log(response);
        },
        error: function (response) {
            console.log(response);
        }
    });
}

// call API，代表已經查看過～
function alreadyChecked(index) {
    $("#background" + index).css("background-color", "#FFFFF");
    var myURL = head_url + "set_notification_check?user_id=" + localStorage.getItem("sessionID") + "&id=" + index;
    //    console.log("已經查看過了～: "+myURL);
    $.ajax({
        url: myURL,
        type: "GET",
        async: false,
        dataType: "json",
        contentType: 'application/json; charset=utf-8',
        success: function (response) {
            console.log("成功回傳");
            //            console.log(response);
            notificationPage = 0;
            getNotification();
        },
        error: function () {
            //            console.log("error");
        }
    });
}

function checkNotification(postId, index) {
    alreadyChecked(index);
    localStorage.setItem("postType", "innerPost");
    localStorage.setItem("singlePostId", postId);
    setPage("mySinglePostFrame");
}
////////////////// 處理通知 END //////////////////


////////////////// 共同討論 START //////////////////
var socket;
function createDiscussRoom(){
    console.log("發起");
    //----- 創建一個共同討論的聊天室 START -----//
    var tags = [{tag_id: "00000",tag_name: "Python"}];
    var data = {tags: tags,
    question: "我想問python的問題", asker:{user_id: localStorage.getItem("sessionID"),incognito: false}};
    console.log("data: ");
    console.log(data);
    socket.emit('create_room' , data);
    socket.on('received_message', function(response) {
        console.log("聊天室頻道: "+response._id);
    })
    //----- 創建一個共同討論的聊天室 END -----//
    
    //----- 找出匹配的人選 START -----//
    var myURL = head_url + "discussion_recommand_user";
    data = {tags: ["00000"]};
    console.log("data: ");
    console.log(data);
    $.ajax({
        url: myURL,
        type: "POST",
        data: JSON.stringify(data),
        async: false,
        dataType: "json",
        contentType: 'application/json; charset=utf-8',
        success: function(response){
            console.log("推薦人選的id");
            console.log(response);
        }
    });
    //----- 找出匹配的人選 END -----//
}

function joinDiscussRoom(){
    console.log("接受");
    var data = {_id: "000001", user_id: localStorage.getItem("sessionID"), incognito: false};
    socket.emit('join_room' , data);
}

////////////////// 共同討論 END //////////////////

window.addEventListener("load", function () {
    start();
    var role = localStorage.getItem("role");
    if (role == "facebook_user" || role == "google_user") {
        setNotification();
        window.fbAsyncInit = function () {
            FB.init({
                appId: '1018939978932508',
                cookie: true,
                xfbml: true,
                version: 'v11.0'
            });

            FB.AppEvents.logPageView();

        };

        (function (d, s, id) {
            var js, fjs = d.getElementsByTagName(s)[0];
            if (d.getElementById(id)) {
                return;
            }
            js = d.createElement(s);
            js.id = id;
            js.src = "https://connect.facebook.net/en_US/sdk.js";
            fjs.parentNode.insertBefore(js, fjs);
        }(document, 'script', 'facebook-jssdk'));
    }
    else {
        if(session_id==undefined){
            document.getElementById("main-menu-header").innerHTML = "";
        }
        document.getElementById("chatImage").innerHTML = "";//聊天圖像
        document.getElementById("chatroom").innerHTML = "";//聊天視窗
        document.getElementById("chatList").innerHTML = "";//聊天列表
        document.getElementById("headerNotification").innerHTML = "";//上方通知
    }
    
    //----- 共同討論 START -----//
    var queryStr = "user_id="+localStorage.getItem("sessionID");
    socket = io('https://soselab.asuscomm.com:55002', {query: queryStr});
    //監聽connect事件可確認是否連上server
    socket.on('connect', function(response) {
      //印出server的回應
      console.log('connect response : ' + response);
    })
    
//    //test
//    socket.on('test', function(response) {
//        console.log("收到socket回應： "+response);
//    });
//    socket.emit('test' , "socket有接上");
    //----- 共同討論 END -----//
}, false);

//window.addEventListener("load", start, false);