# 02_inheritance/notification.py
from abc import ABC, abstractmethod
from datetime import datetime, timezone


# 抽象基底クラス (Abstract Base Class)
class BaseNotification(ABC):
    """
    すべての通知チャネルの親クラス
    ABC を継承することで抽象クラスになる
    """

    def __init__(self, sender_id: str):
        self._sender_id = sender_id

    @property
    def sender_id(self) -> str:
        return self._sender_id

    def _format_message(self, body: str) -> str:
        """共通のメッセージ整形ロジック (具象メソッド) """
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        return f"[{now}] {body}"

    @abstractmethod
    def send(self, recipient: str, body: str) -> bool:
        """
        サブクラスで必ず実装しなければならない抽象メソッド
        実装を忘れるとインスタンス化時に TypeErrorになる
        """


# 具象クラス群 (COncrete Classes)
class EmailNotification(BaseNotification):
    def __init__(self, sender_id: str, smtp_server: str):
        super().__init__(sender_id)
        self._smtp_server = smtp_server

    def send(self, recipient: str, body: str) -> bool:
        # メールアドレスの簡易検証
        if "@" not in recipient:
            print(f"[Email エラー] 無効なメールアドレスです: {recipient}")
            return False

        formatted_body = self._format_message(body)
        print(f"[Email 送信] ({self._smtp_server} 経由)")
        print(f"  To: {recipient}")
        print(f"  Body: {formatted_body}")
        return True


class SlackNotification(BaseNotification):
    def __init__(self, sender_id: str, webhook_url: str):
        super().__init__(sender_id)
        self._webhook_url = webhook_url

    def send(self, recipient: str, body: str) -> bool:
        formatted_body = self._format_message(body)
        # 宛先チャンネルの補正
        channel = recipient if recipient.startswith("#") else f"#{recipient}"
        print(f"[Slack 送信] ({self._webhook_url})")
        print(f"  Channel: {channel}")
        print(f"  Message: {formatted_body}")
        return True


class SmsNotification(BaseNotification):
    def __init__(self, sender_id: str, max_chars: int = 140):
        super().__init__(sender_id)
        self._max_chars = max_chars

    def send(self, recipient: str, body: str) -> bool:
        formatted_body = self._format_message(body)
        if len(formatted_body) > self._max_chars:
            print(
                f"[SMS エラー] 文字数オーバーです ({len(formatted_body)}/{self._max_chars}文字)")
            return False

        print("[SMS 送信]")
        print(f"  To: {recipient}")
        print(f"  Message: {formatted_body}")
        return True


# サービス層 (NotificationService)
class NotificationService:
    """
    一括送信を担当するサービス
    Slack や Email の存在を知らず、BaseNotification にのみ依存する
    """

    def __init__(self):
        self._channels: list[BaseNotification] = []

    def add_channel(self, channel: BaseNotification) -> None:
        self._channels.append(channel)

    def notify_all(self, recipient: str, message: str) -> int:
        """登録されている全チャネルに送信を実行"""
        success_count = 0
        for channel in self._channels:
            if channel.send(recipient, message):
                success_count += 1
        return success_count


# =====================================================================
# 動作確認
# =====================================================================
if __name__ == "__main__":
    print("--- 1. 抽象クラスの強制チェック ---")
    try:
        # 抽象クラスを直接インスタンス化しようとするとエラーになる
        # base = BaseNotification("system_01")
        pass
    except TypeError as e:
        print(f"期待通りのエラー: {e}")

    print("\n--- 2. 各チャネルのセットアップ ---")
    service = NotificationService()
    service.add_channel(EmailNotification(
        sender_id="sys_admin", smtp_server="smtp.example.com"))
    service.add_channel(SlackNotification(
        sender_id="bot_alert", webhook_url="https://hooks.slack.com/..."))
    service.add_channel(SmsNotification(
        sender_id="sms_gateway", max_chars=100))

    print("\n--- 3. 一括送信（ポリモーフィズムの実行） ---")
    total_sent = service.notify_all(
        recipient="user@example.com",
        message="システムエラーが発生しました。確認してください。"
    )
    print(f"\n送信完了: {total_sent} 件成功")
