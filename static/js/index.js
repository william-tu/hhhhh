// 签名
var sign = {};
// 获得全部城市
var cityobj = null;
// 分享数据
var shareData = {};

// 获得距离啥的
var userobj = null;
$('#tijiao').on('click', function(){
  if($('#name').val() == '' && $('#didian').val() == '') {
    alert('请填写信息');
    return ;
  }
  $.ajax({
    type: 'POST',
    url: 'http://william-tu.cn/user',
    // contentType: 'application/json',
    // data to be added to query string:
    data: { 
      name: $('#name').val(),
      from: $('#didian').val()
    },
    
    // type of data we are expecting in return:
    dataType: 'json',
    success: function(data){
      // this.append(data.project.html)
      $('.page-9 .one').text(data.distance);
      $('.page-9 .two').text(data.all_user);
      $('.page-10 .one').text('现价' + data.price + '元');
      $('.page-10 .banmian textarea').val(data.share_url);

      //设置进度条
      $('.process-kuang').css('margin-left', 100 - (data.price*1.0 / data.distance)*100 - 5 + '%' );
      $('.process-huang').css('width', 100 - (data.price*1.0 / data.distance)*100 + '%');
      $.fn.fullpage.moveNext(true);
      userobj = data;
    },
    error: function(xhr, type){
      console.log('Ajax error!');
      alert('网络状况不好，请刷新重试');
    },
  })
});

// 获得全部城市
// var cityobj = null;
$.ajax({
  type: 'GET',
  url: '/static/media/citys.txt',
  dataType: 'json',
  contentType: "application/x-www-form-urlencoded; charset=utf-8",
  success: function(data){
    cityobj = data.provinces;
    console.log(cityobj);
    // for(var i of cityobj){
    //   $('#sheng')
    // }
    cityobj.forEach(function(city, index) {
      $('#sheng').append('<option value='+ index +'>'+ city.provinceName +'</option>');
    });
  },
  error: function(data){
    alert('城市获取失败，请重试');
  }
})

// 选择市
$('#sheng').on('change', function() {
  if($('#sheng').val() !== '' || $('#sheng').val() !== null){
    $('#didian option').remove();
    cityobj[parseInt($('#sheng').val())].citys.forEach(function(city, index) {
      $('#didian').append('<option value='+ city.citysName +'>'+ city.citysName +'</option>');
    });
  }
})

$('#didian, #sheng').on('change', function() {
  $('.page-8 .dizhi span').text($('#didian').val());
})

$('#name').on('change', function() {
  $('.page-8 .huoche .name').text($('#name').val());
})

// 领取
$('#lingqu').on('click', function() {
  // if(userobj.price == 0) 
  alert('请前往湖南省衡阳市华耀碧桂园十里江湾营销中心领取现金红包');
  // else alert('您的火车票还没砍至0元，快邀请小红包来帮忙吧！');
});

// 分享事件

$('#kanjia').on('click', function() {
  $('.page-10 .motai').toggle();
  // var url = 'http://' + location.host + userobj.share_url;
  // location.href = url;
  shareData = {
    appId: sign.app_id,
    signature: sign.sign,
    // timestamp: sign.timestamp,
    // nonceStr: sign.nonceStr,
    // title: '衡阳市华耀碧桂园十里江湾营销中心',
    // desc: '衡阳市华耀碧桂园十里江湾营销中心邀您领取0元火车票',
    link: 'http://' + location.host + userobj.share_url,
    // imgUrl: 'http://' + location.host + '/static/images/01/01.jpg',
  };
  wechat.wechatShare(shareData);
})

$('.guan').on('click', function() {
  $('.page-10 .motai').toggle();
})

// 设置距离时间
var nowTime = new Date();
var chunjie = new Date("2018/2/17 00:00:00");
var dateDiff = chunjie - nowTime;
var tianshu = Math.floor(dateDiff / (24 * 3600 * 1000));
$('.page-7 span').text(tianshu);

// 微信分享
var wechat = {
  // wechatConfig: function (config) {
  //   wx.config({
  //       debug: false,
  //       appId: config.appId,
  //       timestamp: config.timestamp,
  //       nonceStr: config.nonceStr,
  //       signature: config.signature,
  //       jsApiList: config.jsApiList
  //   });
  // },
  wechatShare: function ($shareData) {
    var _default = {   
        debug: false,
        timestamp: timestamp,
        nonceStr: random_str,
        title: '碧桂园助力“携爱回家”',
        desc: '参与h5，好友助力赢取免费回家车票',
        imgUrl: 'http://' + location.host + '/static/images/gongyong/share2.jpg',
        jsApiList: [
            'checkJsApi',
            'onMenuShareTimeline',
            'onMenuShareAppMessage',
            'onMenuShareQQ',
            'onMenuShareWeibo'
        ]
    };

    var config = $.extend(_default, $shareData);
    wx.config({
      debug: false,
      appId: config.appId,
      timestamp: config.timestamp,
      nonceStr: config.nonceStr,
      signature: config.signature,
      jsApiList: config.jsApiList
    });
    wx.ready(function () {
      wx.onMenuShareAppMessage(config);
      wx.onMenuShareTimeline(config);
      wx.onMenuShareQQ(config);
      wx.onMenuShareWeibo(config);
    });
  }
}
//时间戳 签名用
var timestamp = parseInt(new Date().getTime() / 1000) + '';
//随机字符串  签名用
var random_str = Math.random().toString(36).substr(2, 15);;

// 获取id，sign

$.ajax({
  url: 'http://william-tu.cn/sign',
  type: 'POST',
  data: JSON.stringify({
    'url': location.href,
    'timestamp': timestamp,
    'nonce_str': random_str,
  }),
  contentType: 'application/json',
  dataType: 'json',
  success: function(data){
    // sign.app_id = data.app_id;
    // sign.sign = data.sign;
    sign = data
    shareData = {
      appId: sign.app_id,
      signature: sign.sign,
      // timestamp: timestamp,
      // nonceStr: random_str,
      // title: '碧桂园助力“携爱回家”',
      // desc: '参与h5，好友助力赢取免费回家车票',
      link: 'http://' + location.host,
      
    };
    wechat.wechatShare(shareData);
  },
  error: function(data){
    alert('网络状况不好，请刷新重试');
  },
})



