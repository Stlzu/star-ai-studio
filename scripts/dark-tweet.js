// dark-mode-tweet.js — Posts to X.com via Chrome JS injection
// Works 100% without display — no screenshot, no coordinates needed
(function(){
  var text = arguments[0];
  
  var postIt = function() {
    var ta = document.querySelector('[data-testid="tweetTextarea_0"]');
    if (!ta) return 'NO_COMPOSER';
    
    ta.focus();
    ta.innerText = text;
    ta.setAttribute('data-text', text);
    ta.dispatchEvent(new Event('input', {bubbles: true}));
    
    setTimeout(function() {
      var btn = document.querySelector('[data-testid="tweetButton"]');
      if (btn) { btn.click(); return 'POSTED'; }
    }, 2000);
    
    return 'TEXT_SET';
  };
  
  if (window.location.href.indexOf('compose') === -1) {
    window.location.href = 'https://x.com/compose/post';
    setTimeout(postIt, 3000);
  } else {
    return postIt();
  }
})()
