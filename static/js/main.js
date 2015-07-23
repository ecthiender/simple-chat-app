(function() {
  // when the window completes loading everything, execute the init function
  window.onload = function() {
    init();
  };

  var ws, nick;

  // initialize whatever is needed for the app
  var init = function() {
    nick_mgr.init();
  };

  var connection = {
    init: function() {
      ws = new WebSocket('ws://' + window.location.host + '/chat');
      ws.onopen = connection.opened;
      ws.onclose = connection.closed;
      ws.onmessage = chat.message_recvd;
    },
    opened: function() {
      console.log('Connected');
      $('#status').innerHTML = "Connected";
      nick_mgr.send_nick();
      chat.init();
    },
    closed: function() {
      console.log('Disconnected');
      $('#status').innerHTML = "Disconnected!";
    }
  };

  var nick_mgr = {
    init: function() {
      $('#nick').focus();
      $('#save-nick').onclick = this.save;
      $('#nick').onkeypress = this.key_pressed;
    },
    save: function(event) {
      nick = $('#nick').value;
      $('#disp-nick').innerHTML = nick;
      $('#nick-wrapper').style['display'] = 'none';
      connection.init();
    },
    send_nick: function() {
      ws.send(JSON.stringify({'type': 'nick', 'nick': nick}));
    },
    key_pressed: function(event) {
      if(event.keyCode == 13) { // enter is pressed..
        nick_mgr.save();
      }
    }
  };

  var chat = {
    init: function() {
      $('#chat').style['display'] = 'block';
      $('#user-list').style['display'] = 'block';
      $('#send').onclick = this.send_on_click;
      $('#chat-enter').onkeypress = this.send_key_pressed;
      this.$chat_box = $('#chat-box');
      this.focus_chat_enter();
    },
    message_recvd: function(data) {
      var payload = JSON.parse(data.data);
      if(payload.type == 'chat') {
        $('#chat-box').innerHTML += '<b>' + payload.nick + ':</b> ' +
          payload.msg + '<br>';
        $('#chat-box').scrollTop = $('#chat-box').scrollHeight;
      }
      else if(payload.type == 'user-info') {
        $('#online-users').innerHTML = payload.users.join('<br/>');
      }
    },
    send_key_pressed: function(event) {
      //console.log('send key pressed', event.keyCode);
      if(event.keyCode == 13) { // enter is pressed..
        chat.send_msg();
      }
    },
    send_on_click: function(event) {
      chat.send_msg();
    },
    send_msg: function() {
      var msg = $('#chat-enter').value;
      $('#chat-enter').value = '';
      ws.send(JSON.stringify({'type': 'chat', 'nick': nick, 'msg': msg}));
      $('#chat-box').innerHTML += '<b>Me:</b> ' + msg + '<br/>';
      $('#chat-box').scrollTop = $('#chat-box').scrollHeight;
    },
    focus_chat_enter: function() {
      $('#chat-enter').focus();
    }
  };

  // helper functions..
  var $ = function(selector, el) {
    if(!el) {
      el = document;
    }
    return el.querySelector(selector);
  };
})();
