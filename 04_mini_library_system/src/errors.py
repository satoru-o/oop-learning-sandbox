# 04_mini_library_system/errors.py


class LibraryError(Exception):
    """図書館ドメインの基本例外クラス"""


class BookUnavailableError(LibraryError):
    """本が貸出中で借りられない"""

    def __init__(self):
        super().__init__("この本は貸出中です")


class LoanLimitExceededError(LibraryError):
    """貸出冊数の上限超過"""

    def __init__(self, max_loans: int, current: int):
        super().__init__(f"貸出上限を超えます (上限: {max_loans}冊 / 現在: {current}冊)")
        self.max_loans = max_loans
        self.current = current


class UnpaidFeeError(LibraryError):
    """延滞料が未払いで借りられない"""

    def __init__(self, unpaid_fee: int):
        super().__init__(f"延滞料が未払いです ({unpaid_fee}円)")
        self.unpaid_fee = unpaid_fee


class BookNotFoundError(LibraryError):
    """蔵書にない本"""

    def __init__(self, book_id: str):
        super().__init__(f"蔵書にない本です (ID: {book_id})")
        self.book_id = book_id


class MemberNotFoundError(LibraryError):
    """未登録の会員"""

    def __init__(self, member_id: str):
        super().__init__(f"未登録の会員です (ID: {member_id})")
        self.member_id = member_id


class BookNotOnLoanError(LibraryError):
    """貸出中でない本は返却できない"""

    def __init__(self, book_id: str):
        super().__init__(f"この本は貸出中ではありません (ID: {book_id})")
        self.book_id = book_id


class DuplicateBookError(LibraryError):
    """すでに登録されている本のID"""

    def __init__(self, book_id: str):
        super().__init__(f"すでに登録されている本です (ID: {book_id})")
        self.book_id = book_id


class DuplicateMemberError(LibraryError):
    """すでに登録されている会員のID"""

    def __init__(self, member_id: str):
        super().__init__(f"すでに登録されている会員です (ID: {member_id})")
        self.member_id = member_id


class BookReservedError(LibraryError):
    """他の会員が先に予約しているため借りられない"""

    def __init__(self):
        super().__init__("この本は他の会員が予約しています")


class BookAvailableError(LibraryError):
    """借りられる本は予約できない"""

    def __init__(self):
        super().__init__("この本は貸出可能です。予約せずに借りられます")


class DuplicateReservationError(LibraryError):
    """同じ本を二重に予約できない"""

    def __init__(self, member_id: str, book_id: str):
        super().__init__(f"すでに予約しています (会員: {member_id} / 本: {book_id})")
        self.member_id = member_id
        self.book_id = book_id


class AlreadyBorrowedError(LibraryError):
    """自分が借りている本は予約できない"""

    def __init__(self, member_id: str, book_id: str):
        super().__init__(f"すでに借りている本です (会員: {member_id} / 本: {book_id})")
        self.member_id = member_id
        self.book_id = book_id


class ReservationNotFoundError(LibraryError):
    """キャンセルしようとした予約がない"""

    def __init__(self, member_id: str, book_id: str):
        super().__init__(f"予約がありません (会員: {member_id} / 本: {book_id})")
        self.member_id = member_id
        self.book_id = book_id


# 永続化（外界）の例外。業務ルール違反（LibraryError）とは別系統にする
class StorageError(Exception):
    """保存・読み込みに失敗した"""


class CorruptedDataError(StorageError):
    """保存データが壊れている（JSON として不正・版違い・項目の欠落や型の不一致・参照切れ）"""
