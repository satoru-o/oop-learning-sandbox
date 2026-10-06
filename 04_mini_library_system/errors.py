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
