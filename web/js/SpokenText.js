 var u = new SpeechSynthesisUtterance();
 u.text = 'Hello World';
 u.lang = 'en-US';
 u.rate = 1.2;
 u.onend = function(event) { alert('Finished in ' + event.elapsedTime + ' seconds.'); }
 speechSynthesis.speak(u);