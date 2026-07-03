# 种子用户定价与支付 Requirements

## 1. 背景与问题

当前项目已经具备老师端主链路，但还没有正式的付费体系。现在准备引入首批种子用户定价，用于验证真实付费意愿，同时控制产品早期扩散节奏。

当前需要解决的核心问题有四个：

1. 如何明确“前 10 个终身免费、11-50 名 9.9 元终身”的业务口径。
2. 如何避免按注册顺序粗暴发名额，导致无效注册占坑。
3. 如何让支付与权益发放具备一致口径，避免后续接支付时返工。
4. 如何在微信小程序内优先落地首期付费，同时为支付宝等后续渠道预留扩展空间。

## 2. 目标

建设首期可落地的“种子用户定价与支付规则”，用于：

- 支撑前 50 名种子用户活动；
- 在微信小程序内完成首期付费闭环；
- 为后续正式套餐、支付宝支付和后台运营工具打基础；
- 保证名额分配、支付回调、权益发放和人工纠错有统一规则。

## 3. 首期范围

首期必须覆盖以下内容：

- 种子活动名额规则
- 用户资格判定与锁定规则
- 免费资格直接发放规则
- 9.9 元资格的支付与超时释放规则
- 终身权益发放规则
- 后台查看和手动纠错规则
- 支付渠道抽象与首期渠道范围

首期支付落地范围限定为：

- 微信小程序内微信支付
- 支付宝支付通道预留，但不要求本阶段完成前端入口

## 4. 非目标

以下内容不属于首期范围：

- 学校版或机构版套餐
- 包月、包年、按次包等复杂订阅体系
- 积分、优惠券、邀请返现、分销
- 企业级对账中心
- 完整支付宝小程序客户端
- 多端统一支付体验

## 5. 用户画像

### 5.1 主用户

首批体验产品的化学老师。

特点：

- 已经愿意在微信小程序里完成拍题、题库、组卷等操作；
- 对价格敏感，但愿意为省时省力付费；
- 希望规则简单透明，不想理解复杂订阅体系；
- 对“抢先体验名额”和“终身使用”这类承诺更敏感。

### 5.2 维护者

个人开发者本人。

特点：

- 需要知道谁拿到了免费资格，谁拿到了 9.9 资格；
- 需要知道哪些订单未支付、已支付、已释放、需人工修正；
- 需要对少量异常情况进行手动补发、手动关闭、人工纠错。

## 6. 用户故事

1. 作为老师，我希望看到当前种子计划规则，这样我能理解自己是否还能享受免费或 9.9 元终身资格。
2. 作为老师，我希望点击领取资格后系统能立即告诉我自己拿到的是免费、9.9 元还是活动已结束，这样我不用猜。
3. 作为老师，如果我拿到前 10 名免费资格，我希望系统直接为我开通终身权益，而不是还要走支付流程。
4. 作为老师，如果我拿到 9.9 元资格，我希望系统在支付成功后立即开通终身权益。
5. 作为老师，如果我拿到 9.9 元资格但暂时没付，我希望系统规则明确，知道资格会保留多久。
6. 作为个人开发者，我希望后台能看到免费名额、已锁定未支付名额、已支付人数和释放回收人数，这样我能核对活动运行情况。
7. 作为个人开发者，我希望支付回调和权益发放是幂等的，这样重复回调不会造成重复开通。
8. 作为个人开发者，我希望首期先在微信小程序内落地微信支付，同时保留支付宝扩展位，这样不必一开始维护多套客户端入口。

## 7. 业务规则与约束

1. 首期种子活动规则固定为：
   - 前 10 个成功领取资格的用户获得终身免费权益；
   - 第 11-50 个成功领取资格的用户获得 9.9 元终身购买资格；
   - 第 51 个及以后用户不再获得本轮种子活动资格。
2. 名额口径以“成功锁定资格”而不是“注册时间”作为判断标准。
3. 单个用户在同一轮种子活动中最多只能拥有一种资格，不允许重复领取。
4. 免费资格用户不得进入支付流程，系统应直接发放终身权益并记录发放来源。
5. 9.9 元资格用户在支付成功前不得获得终身权益。
6. 9.9 元资格在锁定后应设置支付有效期；超时未支付时，资格应自动释放回名额池。
7. 支付回调处理必须幂等；重复回调不得重复生成权益。
8. 权益发放必须以服务端最终状态为准，前端展示不得作为真实授权来源。
9. 首期前端支付入口限定为微信小程序内微信支付。
10. 支付渠道模型需预留支付宝通道，但不要求本阶段完成支付宝小程序或 H5 支付前端。
11. 后台必须支持对异常订单和异常权益进行人工处理，但人工处理也必须留痕。

## 8. 验收标准

### 8.1 名额与资格

1. When a logged-in teacher clicks to claim the seed offer and free slots are still available, the system shall lock a free seed eligibility for that user and prevent the user from entering any paid flow.
2. When a logged-in teacher clicks to claim the seed offer after the first 10 free eligibilities are exhausted and 9.9 slots are still available, the system shall lock a paid seed eligibility for that user.
3. When a logged-in teacher clicks to claim the seed offer after all 50 seed eligibilities are exhausted, the system shall return a clear “activity ended” result and shall not create any new eligibility.
4. While a user already owns a seed eligibility for the current round, when the user retries claiming, the system shall return the existing result instead of allocating a new slot.

### 8.2 支付与释放

5. When a paid seed eligibility is locked and the user does not complete payment within the configured payment window, the system shall mark the eligibility as expired and release the reserved slot.
6. When a paid seed eligibility holder completes payment successfully through the supported channel, the system shall mark the related order as paid and grant the lifetime entitlement.
7. When the payment callback is retried or delivered multiple times, the system shall keep the order and entitlement state correct without granting duplicate benefits.

### 8.3 权益

8. When a free seed eligibility is granted, the system shall immediately create an active lifetime entitlement for the user with a traceable grant source.
9. When a paid seed order is paid successfully, the system shall create or activate the same lifetime entitlement type used by free seed users, while preserving the different grant source.
10. While a user has no active lifetime entitlement, the system shall not treat a claimed-but-unpaid seed eligibility as a valid paid entitlement.

### 8.4 渠道与后台

11. When the first payment integration is implemented, the system shall support payment initiation inside the WeChat Mini Program through the WeChat payment channel.
12. While Alipay is not yet exposed on the client, the system shall still keep a channel abstraction that allows Alipay to be added later without redesigning eligibility, order, or entitlement rules.
13. When the developer opens the future admin payment view, the system shall be able to show free grants, locked unpaid slots, paid activations, expired reservations, and manual corrections as separate statuses.
