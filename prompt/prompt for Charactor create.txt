我要照著這個步驟進行資料處理的話，應該如何給AI prompt。
假設我的資料都在以下路徑:
https\://github.com/Soyorin322/AI/tree/main/data\_processing/text/Though%20I%20Am%20an%20Inept%20Villainess%20Tale%20of%20the%20Butterfly-Rat%20Body%20Swap%20in%20the%20Maiden%20Court
假設還未標註speaker(目前1-9卷都已經標註完成)，請分為3步驟的prompt給我:

1. 將小說標註speaker，自動在**processed**資料夾中建立對應的資料夾(過去所做到的)
2. 提取**processed**資料夾中標註完成的小說資料，使用Aiko的角色框架作為模板，以Reirin作為建立角色的目標，製作event.json
3. 使用標註speaker的小說以及對應的event.json，建立這個角色的分析資料庫

可以。依照我們剛剛確定的 architecture，我建議把整個流程固定成 **三個彼此獨立的 Prompt**，每一步都有非常明確的 ownership，避免 AI 在同一次工作裡跨層做太多事。

目前正式資料流應是：

```text
Step 1
Raw Novel
↓
Speaker / Thinker Attribution
↓
processed/volume_XX/
   *_speaker標註.md


Step 2
Speaker-grounded Novel
↓
Event Segmentation
↓
processed/volume_XX/events.json


Step 3
Complete Event + Speaker-grounded Novel
↓
Aiko Character Perspective Pre-Analysis
↓
Character Knowledge / Inference
↓
Character Reconstruction
↓
agents/AI_friend/Reirin/
```

這和最新 `data_processing/text/Readme.md` 的兩階段 source processing，以及 Aiko 接手 Perspective / Character Reconstruction 的分工一致。

下面三份我會寫成**可以直接複製貼給 Codex / GitHub AI Agent 使用的 Prompt**。

---

# Prompt 1：小說 Speaker / Thinker Attribution

這一步**只做 Speaker / Thinker**。

不要建立 Event，不要分析人格，不要判斷角色知道什麼。

> ## Task — Text Stage 1: Speaker / Thinker Attribution
>
> Repository:
>
> `Soyorin322/AI`
>
> Source directory:
>
> `data_processing/text/Though I Am an Inept Villainess Tale of the Butterfly-Rat Body Swap in the Maiden Court/`
>
> 請先閱讀並遵守：
>
> `data_processing/README.md`
>
> `data_processing/text/Readme.md`
>
> 如果 repository 中存在 speaker attribution guideline，也請一併閱讀。
>
> ---
>
> ### 目標
>
> 對 Source directory 中尚未完成 Speaker / Thinker Attribution 的小說檔案進行 Stage 1 處理。
>
> 此工作只負責：
>
> 1. dialogue speaker attribution
> 2. inner-thought thinker attribution
>
> 不要建立 Event。
>
> 不要分析角色人格。
>
> 不要建立 Memory、Evidence、Period Character State。
>
> 不要判斷某角色知道什麼或不知道什麼。
>
> ---
>
> ### Output directory
>
> 不要修改原始小說。
>
> 自動在：
>
> `data_processing/text/Though I Am an Inept Villainess Tale of the Butterfly-Rat Body Swap in the Maiden Court/processed/`
>
> 建立對應卷數資料夾：
>
> ```text
> processed/
> ├── volume_01/
> ├── volume_02/
> ├── volume_03/
> └── ...
> ```
>
> 每個輸入檔案建立一份 speaker-grounded derivative。
>
> 例如：
>
> ```text
> 惡女不才_volume5_part1.md
> ↓
> processed/volume_05/
> 惡女不才_volume5_part1_speaker標註.md
> ```
>
> 如果一卷沒有拆 part：
>
> ```text
> 惡女不才_volume1.md
> ↓
> processed/volume_01/
> 惡女不才_volume1_speaker標註.md
> ```
>
> ---
>
> ### Speaker attribution rules
>
> 所有實際 dialogue 都應在來源支持的情況下標示 speaker。
>
> 例如：
>
> ```text
> 玲琳: 「……」
> ```
>
> 在換身期間，必須分離「角色身份」與「身體身份」：
>
> ```text
> 玲琳（身體：朱慧月）: 「……」
> 慧月（身體：黃玲琳）: 「……」
> ```
>
> 換身結束後不得繼續保留錯誤的 body label。
>
> ---
>
> ### Inner thought rules
>
> 所有真正的 inner thought，包括：
>
> ```text
> （……）
> ```
>
> 都必須在來源支持時標示 thinker。
>
> 例如：
>
> ```text
> 玲琳（身體：朱慧月）:（我還活著……）
> ```
>
> 不得留下可明確判斷 thinker 的 bare inner thought。
>
> ---
>
> ### Narration
>
> 普通 narration 不要加 speaker。
>
> 例如：
>
> ```text
> 玲琳抬起頭望向天空。
> ```
>
> 必須保持原樣。
>
> ---
>
> ### Attribution evidence priority
>
> Speaker / thinker 判斷優先使用：
>
> ```text
> 1. explicit narrative attribution
> 2. current scene participants
> 3. dialogue turn structure
> 4. addressee
> 5. nearby narration / coreference
> 6. character-specific knowledge
> 7. body-swap / disguise state
> 8. speech style only as weak tie-breaker
> ```
>
> 不得只因「這句話很像某角色」就強制標註。
>
> ---
>
> ### Uncertainty
>
> 如果來源不足以可靠決定 speaker：
>
> ```text
> 【speaker 不確定（候選：A / B）】: 「……」
> ```
>
> 如果 thinker 無法可靠判定：
>
> ```text
> 【thinker 不確定（候選：A / B）】:（……）
> ```
>
> 寧可保留 uncertainty，不要猜測。
>
> ---
>
> ### Source-integrity invariant
>
> Speaker attribution 只能新增 attribution prefix。
>
> **禁止修改小說正文。**
>
> 每個輸出檔完成後必須驗證：
>
> ```text
> remove all inserted attribution prefixes
> ↓
> reconstructed source
> ==
> original source
> ```
>
> 必須逐字一致。
>
> 不得：
>
> * 改寫
> * 摘要
> * 修正文法
> * 更換標點
> * 調整段落
> * 改變行序
>
> ---
>
> ### Processing order
>
> 逐檔處理。
>
> 一個檔案完成：
>
> 1. 執行 source-integrity validation
> 2. 寫入對應 `processed/volume_XX/`
> 3. 確認輸出存在
> 4. 再處理下一個檔案
>
> 不要等全部小說處理完成後才一次寫入。
>
> ---
>
> ### Final report
>
> 對每個檔案回報：
>
> ```text
> input
> output
> dialogue count
> thought count
> uncertain speaker count
> uncertain thinker count
> body-swap label count
> source-integrity validation: PASS / FAIL
> ```
>
> 如果 validation FAIL，停止處理該檔案，不得將其視為完成。

這一份本質上就是我們之前 Volume 5～9 做過的工作，但把規則寫成正式可重複使用的版本。

---

# Prompt 2：從 Speaker-grounded Novel 建立 Event Index

這一步非常重要：**雖然最終要建立 Reirin，但 Event 不准變成 Reirin-specific Event。**

這和現在 `data_processing` 的正式 ownership 一致：完整 story-level Event 屬於 `data_processing`，Character Perspective 從 Aiko 才開始。

> ## Task — Text Stage 2: Complete Story-Level Event Indexing
>
> Repository:
>
> `Soyorin322/AI`
>
> Source root:
>
> `data_processing/text/Though I Am an Inept Villainess Tale of the Butterfly-Rat Body Swap in the Maiden Court/`
>
> Processed source root:
>
> `data_processing/text/Though I Am an Inept Villainess Tale of the Butterfly-Rat Body Swap in the Maiden Court/processed/`
>
> Future target character:
>
> `黃玲琳 / Reirin`
>
> ---
>
> ### Read before execution
>
> 必須先閱讀：
>
> ```text
> data_processing/README.md
> data_processing/text/Readme.md
> agents/AI_friend/Aiko/docs/folder_ownership.md
> agents/AI_friend/Aiko/docs/reconstruction.md
> agents/AI_friend/Aiko/docs/research/event/character_perspective_preanalysis_v0.0.1.md
> ```
>
> Aiko docs 在這一步只用來確認 downstream contract。
>
> **不要在這一步執行 Character Perspective 或 Character Reconstruction。**
>
> ---
>
> ### Input
>
> 僅使用：
>
> ```text
> processed/volume_XX/
> *_speaker標註.md
> ```
>
> 作為 Event segmentation 的輸入。
>
> 優先使用已完成 human review 的 speaker-grounded source。
>
> ---
>
> ### Goal
>
> 對每一卷建立：
>
> ```text
> processed/volume_XX/events.json
> ```
>
> `events.json` 是：
>
> > complete story-level Event index
>
> 不是小說摘要。
>
> 不是角色視角資料。
>
> 不是 Reirin-specific reconstruction。
>
> ---
>
> ### Critical rule
>
> ```text
> Event = complete source index
> not replacement text
> not character-filtered text
> ```
>
> 每個 Event 必須 deterministic 地返回其完整原文。
>
> ---
>
> ### Reirin must NOT control Event segmentation
>
> 雖然後續目標角色是 Reirin，但這一步：
>
> **不得只建立與 Reirin 有關的 Event。**
>
> **不得因 Reirin 是否在場而改變 Event boundary。**
>
> **不得刪除 Reirin 不知道的故事內容。**
>
> Event segmentation 必須描述作品本身。
>
> 同一份 `events.json` 未來應可以給：
>
> ```text
> Reirin
> Keigetsu
> Yaoming
> Chenyu
> ...
> ```
>
> 使用。
>
> ---
>
> ### Event boundary
>
> Event 是 meaningful story occurrence。
>
> 不要機械使用：
>
> ```text
> one paragraph = one Event
> one chapter = one Event
> one dialogue = one Event
> ```
>
> 可以考慮以下 boundary signals：
>
> ```text
> meaningful action change
> decision
> participant-set change
> location change
> conflict / goal transition
> result / consequence
> causal transition
> identity / body-state transition
> temporal transition
> ```
>
> Event 不宜過細，也不宜把多個明確不同的故事事件合成一筆。
>
> ---
>
> ### Required Event information
>
> 第一版保持最小 schema。
>
> 每個 Event 至少需要：
>
> ```json
> {
>   "event_id": "V01-E-0001",
>   "source_ranges": [
>     {
>       "file": "...",
>       "start_line": 100,
>       "end_line": 150
>     }
>   ],
>   "narrative_order": 1
> }
> ```
>
> 可以加入：
>
> ```text
> label
> section / chapter
> participants
> story_chronology
> ```
>
> 但只有在 source directly supports 或確實有 navigation / downstream value 時才加入。
>
> ---
>
> ### `label`
>
> `label` 只供人類導航。
>
> ```text
> label ≠ evidence
> ```
>
> 不得讓後續 Character Reconstruction 使用 Event label 取代原文。
>
> ---
>
> ### Participants
>
> 可以保存 source-supported participants。
>
> 但：
>
> ```text
> participant
> ≠
> character knowledge
> ```
>
> 不得在這一步建立：
>
> ```text
> character_access
> Accessible
> Inaccessible
> Uncertain
> Known
> Believed
> Suspected
> Misunderstood
> ```
>
> 這些全部屬於 Aiko。
>
> ---
>
> ### Full source preservation
>
> 每個 Event 的 `source_ranges` 必須能返回**完整 Event passage**。
>
> 不得建立：
>
> ```text
> Reirin-readable lines only
> ```
>
> 不得建立：
>
> ```text
> character_access line allow-list
> ```
>
> 不得因某些內容是他人 inner thought 就從 Event 中刪除。
>
> 完整 Event 中可以同時存在：
>
> ```text
> public dialogue
> observable action
> private thought
> narrator information
> hidden information
> ```
>
> Aiko 之後負責區分 Character Perspective。
>
> ---
>
> ### Ordering
>
> 必須保留：
>
> ```text
> narrative_order
> ```
>
> 如果作品有 flashback / retrospective material，必要時加入：
>
> ```text
> story_chronology
> ```
>
> 兩者不得混為一談。
>
> ---
>
> ### Validation
>
> 完成每卷後驗證：
>
> 1. `event_id` unique
> 2. `narrative_order` deterministic
> 3. 所有 source locator 均存在
> 4. 所有 range 位於對應 source file 內
> 5. locator 能返回完整原文
> 6. Event 之間沒有因錯誤 segmentation 造成大量無意義重疊
> 7. 沒有 `character_access` 或 character-specific filtering
> 8. 沒有 personality / Memory / belief / appraisal 資料
>
> ---
>
> ### Output
>
> 每卷建立：
>
> ```text
> processed/
> └── volume_XX/
>     ├── *_speaker標註.md
>     └── events.json
> ```
>
> 每卷完成後單獨保存，再繼續下一卷。
>
> ---
>
> ### Final report
>
> 回報：
>
> ```text
> volume
> input source file(s)
> Event count
> source coverage
> chronology metadata count
> unresolved Event-boundary cases
> validation result
> ```
>
> 如果有不確定 Event boundary，保留可 review 的說明，不要假裝已經確定。

這一步完成後，資料應該長這樣：

```text
processed/
├── volume_01/
│   ├── 惡女不才_volume1_speaker標註.md
│   └── events.json
│
├── volume_02/
│   ├── 惡女不才_volume2_speaker標註.md
│   └── events.json
│
...
```

---

# Prompt 3：建立 Reirin Character Analysis Database

這才真正開始：

> 「玲琳知道什麼？」
> 「她不知道什麼？」
> 「她如何理解？」
> 「這對她的人格、Memory、Relationship、Development 有什麼證據？」

目前 Aiko 已正式把 `CharacterPerspectivePreAnalysis` 放在 Event 與 Character Interpretation 之間。

而 `Accessible / Inaccessible / Uncertain` **只是 perspective analysis guidance**；完整 Event 永遠仍是 analysis source，並且必須能透過 `event_id → source_ranges → original source` 回到 Canon。

> ## Task — Build Reirin Character Analysis Database with Aiko
>
> Repository:
>
> `Soyorin322/AI`
>
> Target character:
>
> ```text
> 黃玲琳
> Character ID: Reirin
> ```
>
> Character output root:
>
> ```text
> agents/AI_friend/Reirin/
> ```
>
> Source:
>
> ```text
> data_processing/text/Though I Am an Inept Villainess Tale of the Butterfly-Rat Body Swap in the Maiden Court/processed/
> ```
>
> Use both:
>
> ```text
> *_speaker標註.md
> events.json
> ```
>
> ---
>
> ### Read before execution
>
> 在建立任何 Reirin 資料前，完整閱讀目前 repository 中最新版本的：
>
> ```text
> agents/AI_friend/Aiko/AGENTS.md
> agents/AI_friend/Aiko/README.md
> agents/AI_friend/Aiko/docs/architecture/character_create_v0.0.8.txt
> agents/AI_friend/Aiko/docs/folder_ownership.md
> agents/AI_friend/Aiko/docs/reconstruction.md
> agents/AI_friend/Aiko/docs/research/event/character_perspective_preanalysis_v0.0.1.md
> agents/AI_friend/Aiko/docs/schemas/
> ```
>
> 並檢查：
>
> ```text
> agents/AI_friend/Reirin/
> ```
>
> 現有結構。
>
> 目前 Aiko contracts 與 docs 優先於舊 Task 文件。
>
> 不得因舊 task 使用較早 schema 就重新導入已 superseded 的：
>
> ```text
> character_access hard filtering
> character-only Event copy
> sparse source replacement
> ```
>
> ---
>
> ### Goal
>
> 使用 Aiko framework 對 Reirin 建立 character-specific analysis database。
>
> Pipeline：
>
> ```text
> Complete Event
> ↓
> Character Perspective Pre-Analysis
> ↓
> Character Knowledge / Inference
> ↓
> Character Interpretation
> ↓
> Evidence
> ↓
> Period Character State
> ↓
> Memory / Development / Compiled Character State
> ```
>
> ---
>
> # Stage A — Character Perspective Pre-Analysis
>
> 對每個可能和 Reirin reconstruction 有關的 Event：
>
> **必須讀取完整 Event 原文。**
>
> Input：
>
> ```text
> Complete Event source
> + speaker / thinker annotation
> + target character = Reirin
> + event metadata
> + necessary previous validated context
> ```
>
> 不得先刪除任何 Event source lines。
>
> ---
>
> ### Perspective prompt
>
> 對完整 Event 判斷：
>
> ```text
> Accessible
> Inaccessible
> Uncertain
> ```
>
> 定義：
>
> **Accessible**
>
> Reirin 在當時可以直接取得的資訊，例如：
>
> ```text
> own action
> own speech
> own explicit thought
> speech directly heard
> observable action / event
> explicitly received information
> own bodily experience
> directly experienced environment
> ```
>
> **Inaccessible**
>
> 完整 Event 中存在，但 Reirin 當時無法知道，例如：
>
> ```text
> another character's private thought
> private conversation while Reirin is absent
> narrator-only omniscient explanation
> future revelation
> hidden motive
> information learned only later
> ```
>
> **Uncertain**
>
> Source 無法可靠判斷，例如：
>
> ```text
> unclear whether Reirin heard something
> ambiguous visibility
> uncertain presence
> unclear temporal accessibility
> ```
>
> 不得強迫 uncertain case 變成 Accessible 或 Inaccessible。
>
> ---
>
> ### Critical PICTURE-style rule
>
> `Accessible / Inaccessible / Uncertain` 只是：
>
> ```text
> analysis guidance
> perspective judgment
> prompt constraint
> ```
>
> **不是 source filter。**
>
> 分析模型仍然取得完整 Event。
>
> 必須始終保持：
>
> ```text
> Complete Event
> +
> Perspective guidance
> ```
>
> 而不是：
>
> ```text
> Complete Event
> ↓
> delete Inaccessible
> ↓
> truncated Event
> ```
>
> ---
>
> ### Provenance
>
> 每一筆 Perspective result 必須保留：
>
> ```text
> event_id
> ↓
> events.json source_ranges
> ↓
> speaker-grounded source
> ↓
> original Canon passage
> ```
>
> `Accessible / Inaccessible / Uncertain` 不得成為 replacement source。
>
> ---
>
> # Stage B — Character Knowledge / Inference
>
> Perspective 與 Character Inference 必須分開。
>
> ```text
> Accessible information
> ≠
> what Reirin concludes from it
> ```
>
> 第二階段可以使用：
>
> ```text
> Complete Event
> + Perspective result
> + validated prior Character State
> + prior Memory
> + prior Knowledge
> + relationship context
> ```
>
> 判斷：
>
> ```text
> Known
> Believed
> Suspected
> Misunderstood
> ```
>
> 不得把：
>
> ```text
> suspicion → known
> belief → objective truth
> reader knowledge → Reirin knowledge
> ```
>
> 自動升級。
>
> ---
>
> # Stage C — Character Interpretation
>
> 只有完成 Perspective / Knowledge gate 後，才可以分析：
>
> ```text
> motivation
> values
> beliefs
> relationships
> emotion
> conflict
> personality
> behavior pattern
> appraisal
> development
> ```
>
> Character Interpretation 必須建立在：
>
> ```text
> Reirin's epistemic state at that time
> ```
>
> 而不是 omniscient reader state。
>
> ---
>
> ### Evidence rule
>
> 所有 character claims 必須有 provenance。
>
> ```text
> Source
> ↓
> Event
> ↓
> Perspective / Knowledge State
> ↓
> Candidate Interpretation
> ↓
> Evidence / Counterevidence
> ↓
> possible Character State
> ```
>
> 核心規則：
>
> ```text
> Plausibility is not canon.
> ```
>
> AI 認為「很合理」不能自動成為 Character Fact。
>
> ---
>
> ### Circularity prevention
>
> 禁止：
>
> ```text
> behavior
> ↓
> infer trait X
> ↓
> trait X explains same behavior
> ↓
> same behavior is treated as new proof of X
> ```
>
> Source evidence、interpretation、hypothesis、consolidated Character State 必須保持可區分。
>
> ---
>
> ### Temporal processing
>
> 必須使用 Event 的：
>
> ```text
> narrative_order
> story_chronology
> ```
>
> 區分：
>
> ```text
> reader learns X now
> ≠
> Reirin knew X then
> ```
>
> Flashback 不得造成 future-knowledge leakage。
>
> ---
>
> ### Body-swap handling
>
> 黃玲琳 / 朱慧月換身期間必須始終區分：
>
> ```text
> character identity
> body identity
> ```
>
> Character reconstruction subject 永遠是：
>
> ```text
> 黃玲琳 / Reirin
> ```
>
> 即使當時她使用：
>
> ```text
> 朱慧月的身體
> ```
>
> 也不能錯誤把慧月的人格／經驗歸給 Reirin。
>
> ---
>
> ### Persistent output
>
> 所有 Reirin-specific artifacts 寫入：
>
> ```text
> agents/AI_friend/Reirin/
> ```
>
> 並依目前最新：
>
> ```text
> agents/AI_friend/Aiko/docs/folder_ownership.md
> ```
>
> 決定實際位置。
>
> 預期概念分類至少包含：
>
> ```text
> reconstruction/
> ├── perspective/
> ├── evidence/
> ├── periods/
> └── development/
>
> character/
> └── compiled / character-state artifacts
>
> memory/
> └── Reirin memory artifacts
> ```
>
> 不要複製 story-level `events.json` 到 Reirin。
>
> Reirin artifacts 只 reference：
>
> ```text
> event_id
> ```
>
> Story-level Event 的 authoritative copy 永遠留在：
>
> ```text
> data_processing/.../processed/volume_XX/events.json
> ```
>
> ---
>
> ### Human review output
>
> 對每一卷產生可重新生成的 review Markdown，例如：
>
> ```text
> reirin_perspective_review_volume01.md
> ```
>
> 每個 Event 至少顯示：
>
> ```text
> Event ID
> source locator
>
> Accessible
> Inaccessible
> Uncertain
>
> Known
> Believed
> Suspected
> Misunderstood
> ```
>
> 以及：
>
> ```text
> [ ] Access boundary checked
> [ ] No private-thought leakage
> [ ] No future-knowledge leakage
> [ ] Known vs Believed/Suspected checked
> [ ] Uncertain cases reviewed
> ```
>
> 這份 Markdown：
>
> ```text
> review artifact
> ≠
> canonical database
> ```
>
> ---
>
> ### Processing order
>
> 必須按照 story chronology / source structure 分批處理。
>
> 建議：
>
> ```text
> Volume 1
> ↓
> Perspective review
> ↓
> validation
> ↓
> Character reconstruction update
> ↓
> Volume 2
> ↓
> ...
> ```
>
> 不要一次讀完 9 卷後直接生成一份最終人格描述。
>
> 必須保留角色隨時間的狀態與發展。
>
> ---
>
> ### Validation
>
> 每一卷完成後至少檢查：
>
> ```text
> Event references resolve
> source ranges resolve
> complete Event remains available
> no character-filtered Event copies
> no private-thought leakage
> no future-knowledge leakage
> uncertainty preserved
> Known / Believed / Suspected distinct
> evidence has provenance
> no circular self-support
> no duplicate story Event
> ```
>
> 如果目前 Aiko validation contracts 已經提供 validator，使用現有 validator，不要另建平行 schema。
>
> ---
>
> ### Final goal
>
> 產物不是：
>
> ```text
> 一份「玲琳個性摘要」
> ```
>
> 而是：
>
> ```text
> Canon
> ↓
> Event
> ↓
> Reirin Perspective
> ↓
> Reirin Knowledge / Belief
> ↓
> Evidence
> ↓
> Historical Character State
> ↓
> Memory / Development
> ↓
> Compiled Reirin Character
> ```
>
> 所有重要 conclusions 必須能一路 trace 回原始小說。

---

## 三個 Prompt 的真正分界

我建議你未來牢記這個判斷方式：

| Prompt        | AI 回答的問題                   |
| ------------- | -------------------------- |
| **1 Speaker** | 「這句話／心理話是誰的？」              |
| **2 Event**   | 「作品中這裡發生了一個什麼範圍的事件？」       |
| **3 Aiko**    | 「對玲琳而言，她知道什麼，以及這些經歷如何形成她？」 |

也就是：

```text
Prompt 1
SOURCE TEXT
→ linguistic grounding

Prompt 2
SOURCE TEXT
→ story structure

Prompt 3
STORY
→ character-specific reconstruction
```

其中有一點我特別建議你**不要寫進 Prompt 2**：

> 「只提取與 Reirin 有關的 Event。」

這會重新把 Character Perspective 污染到 `data_processing`。

正確的是：

```text
Prompt 2:
建立作品完整 Event index

Prompt 3:
從完整 Event 中，以 Reirin 為 target 做 Perspective + Reconstruction
```

這樣你的《惡女不才》1～9 卷資料處理完成之後，同一套：

```text
speaker-grounded novel
+
events.json
```

未來要建立慧月時完全不用重新做前兩步，只需要重新執行：

```text
Prompt 3
Target = Keigetsu
```

這正是現在這套 architecture 最有價值的地方。
