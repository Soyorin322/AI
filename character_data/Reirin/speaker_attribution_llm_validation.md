# Reirin Speaker Attribution — Context Model Validation

Model: `ggml-org/Qwen3-4B-GGUF` / `Qwen3-4B-Q4_K_M.gguf`

Volume 1 is the user-corrected gold reference.

- Gold quotes matched: **1282**
- Non-unknown precision: **55.80%**
- Automatic coverage: **35.65%**
- Correct: **255**
- Wrong: **202**
- Unknown: **825**

## First errors

- raw line 81: predicted `女官`, gold `雅媚` — `「好啦，看呀。是彗星呢。而且，連流星也。這是何等吉祥之兆呀。」`
- raw line 93: predicted `玲琳`, gold `慧月` — `「討厭的女人，消失吧……！」`
- raw line 94: predicted `堯明`, gold `玲琳` — `「呀——！」`
- raw line 99: predicted `堯明`, gold `女官` — `「誰來！ 鷲官，快來救人！」`
- raw line 341: predicted `慧月`, gold `辰宇` — `「妳明不明白的？妳正和飢餓的野獸關在同一個籠子里哦？」`
- raw line 342: predicted `慧月`, gold `玲琳` — `「是這樣呢……要是被那牙齒貫穿，會死的呢。」`
- raw line 347: predicted `慧月`, gold `辰宇` — `「……妳不怕死嗎？」`
- raw line 348: predicted `慧月`, gold `玲琳` — `「畢竟我習慣了。」`
- raw line 354: predicted `慧月`, gold `unknown` — `「喂，野獸沒襲擊人啊。」`
- raw line 355: predicted `慧月`, gold `unknown` — `「朱慧月是無罪的嗎？」`
- raw line 356: predicted `慧月`, gold `unknown` — `「確實，並沒人看到她推人的那一刻。」`
- raw line 357: predicted `慧月`, gold `unknown` — `「但是，那個情形怎麼看都是……」`
- raw line 362: predicted `堯明`, gold `辰宇` — `「……但是，那樣做的話儀式的嚴正性」`
- raw line 365: predicted `慧月`, gold `堯明` — `「這是先前嘲弄玲琳的加罰。」`
- raw line 393: predicted `慧月`, gold `辰宇` — `「嗯……？」`
- raw line 394: predicted `慧月`, gold `unknown` — `「欸……？獅·子·那·邊·倒了……？」`
- raw line 396: predicted `慧月`, gold `玲琳` — `「所以我才說不可以的……不，這也是我的罪過吧……抱歉……」`
- raw line 398: predicted `慧月`, gold `unknown` — `「這……獅子、死了嗎……？」`
- raw line 400: predicted `慧月`, gold `unknown` — `「換言之，這算儀式結束了吧？」`
- raw line 401: predicted `慧月`, gold `unknown` — `「不該如此嗎？畢竟，其中一方已經死了。」`
- raw line 402: predicted `慧月`, gold `unknown` — `「如此說來，朱慧月果然是無罪的嗎……？」`
- raw line 404: predicted `慧月`, gold `辰宇` — `「喂，朱慧月。站得起來嗎？我要確認下獅子的死亡。離開那裡。」`
- raw line 407: predicted `慧月`, gold `辰宇` — `「早有準備嗎？」`
- raw line 408: predicted `慧月`, gold `玲琳` — `「不。這完全是個不幸的事故！」`
- raw line 409: predicted `慧月`, gold `辰宇` — `「事故？」`
- raw line 412: predicted `慧月`, gold `辰宇` — `「在牢里爬行的老鼠？因為想要弔唁，所以藏在袖子里？」`
- raw line 413: predicted `慧月`, gold `玲琳` — `「是的。畢竟是因為我的紕漏而失去了生命。」`
- raw line 415: predicted `慧月`, gold `玲琳` — `「可是，沒能料想到會對遺骸有反應……其結果，奪去了兩隻動物的生命，對此我發自內心反省著。」`
- raw line 421: predicted `慧月`, gold `辰宇` — `「……至少如果有酌情餵食的話，獅子也許就能做出更為冷靜的判斷了吧。」`
- raw line 430: predicted `玲琳`, gold `慧月` — `「怎麼會……」`

**Generation aborted:** validation threshold not met; existing Volume 2/3 files were not replaced.
