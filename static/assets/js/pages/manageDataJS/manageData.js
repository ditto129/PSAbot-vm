function start(){
    var myURL = head_url + "query_faq_update";
    $.ajax({
        url: myURL,
        type: "POST",
        data: JSON.stringify(null),
        async: false,
        dataType: "json",
        contentType: 'application/json; charset=utf-8',
        success: function(response){
            console.log("成功: FAQ數據（query_faq_update）");
            console.log(response);
            $("#dataNum").val(response.data_number);
            $("#dataCycle").val(response.update_cycle);
        },
        error: function(response){
            console.log("失敗: FAQ數據（query_faq_update）");
            console.log(response);
        }
    });
}

function save(){
    var num = $("#dataNum").val();
    if(num==""){
        document.getElementById("resultTitle").innerHTML = "請輸入資料筆數";
        $('#manageDataResult').modal('show');
    }
    else{
        var cycle = $("#dataCycle").val();
        var data = {num: num, cycle: cycle};
        console.log("data: ");
        console.log(data);

        var myURL = head_url + "adjust_faq_update";
        $.ajax({
            url: myURL,
            type: "POST",
            data: JSON.stringify(data),
            async: false,
            dataType: "json",
            contentType: 'application/json; charset=utf-8',
            success: function(response){
                console.log("成功: 更新週期（adjust_faq_update）");
                console.log(response);
                if(response.error != undefined){
                    console.log("something error");
                    document.getElementById("resultTitle").innerHTML = "資料儲存失敗，請再試一次";
                }
                else{
                    document.getElementById("resultTitle").innerHTML = "資料儲存成功";
                }
            },
            error: function(response){
                console.log("失敗: 更新週期（adjust_faq_update）");
                console.log(response);
            }
        });
        // 結果是否成功
        $('#manageDataResult').modal('show');
    }
}

window.addEventListener("load", start, false);