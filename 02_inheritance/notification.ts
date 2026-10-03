// 抽象基底クラス (Abstract Base Class) ---
export abstract class BaseNotification {
  // protected: サブクラスからのみアクセス可能
  constructor(protected readonly senderId: string) { }

  /**
   * 共通のメッセージ整形ロジック（具象メソッド）
   */
  protected formatMessage(body: string): string {
    const now = new Date().toLocaleString("ja-JP");
    return `[${now}] ${body}`;
  }

  /**
   * サブクラスで必ず実装しなければならない抽象メソッド。
   * シグネチャ（引数と戻り値の型）のみを定義する。
   */
  public abstract send(recipient: string, body: string): boolean;
}

// 具象クラス群 (Concrete Classes) ---
export class EmailNotification extends BaseNotification {
  constructor(
    senderId: string,
    private readonly smtpServer: string
  ) {
    super(senderId); // 親クラスのコンストラクタを呼び出す
  }

  public send(recipient: string, body: string): boolean {
    if (!recipient.includes("@")) {
      console.log(`[Email エラー] 無効なメールアドレスです: ${recipient}`);
      return false;
    }

    const formattedBody = this.formatMessage(body);
    console.log(`[Email 送信] (${this.smtpServer} 経由)`);
    console.log(`  To: ${recipient}`);
    console.log(`  Body: ${formattedBody}`);
    return true;
  }
}

export class SlackNotification extends BaseNotification {
  constructor(
    senderId: string,
    private readonly webhookUrl: string
  ) {
    super(senderId);
  }

  public send(recipient: string, body: string): boolean {
    const formattedBody = this.formatMessage(body);
    const channel = recipient.startsWith("#") ? recipient : `#${recipient}`;
    console.log(`[Slack 送信] (${this.webhookUrl})`);
    console.log(`  Channel: ${channel}`);
    console.log(`  Message: ${formattedBody}`);
    return true;
  }
}

export class SmsNotification extends BaseNotification {
  constructor(
    senderId: string,
    private readonly maxChars: number = 140
  ) {
    super(senderId);
  }

  public send(recipient: string, body: string): boolean {
    const formattedBody = this.formatMessage(body);
    if (formattedBody.length > this.maxChars) {
      console.log(`[SMS エラー] 文字数オーバーです (${formattedBody.length}/${this.maxChars}文字)`);
      return false;
    }

    console.log(`[SMS 送信]`);
    console.log(`  To: ${recipient}`);
    console.log(`  Message: ${formattedBody}`);
    return true;
  }
}

// サービス層 (NotificationService) ---
export class NotificationService {
  private readonly channels: BaseNotification[] = [];

  public addChannel(channel: BaseNotification): void {
    this.channels.push(channel);
  }

  public notifyAll(recipient: string, message: string): number {
    let successCount = 0;
    for (const channel of this.channels) {
      // BaseNotification 型として扱うため、具体的なクラスを知らなくても send() を呼び出せる
      if (channel.send(recipient, message)) {
        successCount++;
      }
    }
    return successCount;
  }
}

// =====================================================================
// 動作確認
// =====================================================================
function main() {
  console.log("--- 1. 抽象クラスのコンパイルチェック ---");
  // 抽象クラスを直接インスタンス化しようとするとコンパイルエラー（赤波線）になります：
  // const base = new BaseNotification("sys_01");
  // TS Error: Cannot create an instance of an abstract class.

  console.log("\n--- 2. 各チャネルのセットアップ ---");
  const service = new NotificationService();
  service.addChannel(new EmailNotification("sys_admin", "smtp.example.com"));
  service.addChannel(new SlackNotification("bot_alert", "https://hooks.slack.com/..."));
  service.addChannel(new SmsNotification("sms_gateway", 100));

  console.log("\n--- 3. 一括送信（ポリモーフィズムの実行） ---");
  const totalSent = service.notifyAll(
    "user@example.com",
    "システムエラーが発生しました。確認してください。"
  );
  console.log(`\n送信完了: ${totalSent} 件成功`);
}

main();