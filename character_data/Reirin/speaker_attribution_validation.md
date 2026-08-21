# Reirin Speaker Attribution Validation

The manually corrected Volume 1 is used as a gold reference for validating the conservative scene-aware rules before generating Volume 2 and 3.

- Volume 1 non-abstained precision: **81.25%**
- Volume 1 automatic coverage: **1.24%**
- Correct labelled quotes: **13**
- Wrong labelled quotes: **3**

## Generated volumes

- Volume 2: 1493 quote lines; 810 left as `speaker 不確定` (54.25%).
- Volume 3: 1806 quote lines; 987 left as `speaker 不確定` (54.65%).

## First validation errors

- predicted `堯明`, gold `女官`: `「誰來！ 鷲官，快來救人！」`
- predicted `慧月`, gold `堯明`: `「鷲官長立刻將玲琳救出。剩下的鷲官，將這個女人——朱慧月抓起來！」`
- predicted `冬雪`, gold `玲琳`: `「是，我是一隻溝鼠！」`

The objective is precision-first attribution. Unknown labels are preferred to unsupported speaker assignments.
