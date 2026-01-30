"""Book manager module for ReadAlongBuddy - book creation, library, navigation."""

import datetime
import io
import base64
from PIL import Image
from dataclasses import dataclass, field


@dataclass
class BookPage:
    """A single page in a book."""
    image: Image.Image
    text: str = ""
    ocr_done: bool = False


@dataclass
class Book:
    """A book containing multiple pages."""
    title: str
    pages: list[BookPage] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    current_page: int = 0

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def cover_image(self) -> Image.Image | None:
        if self.pages:
            return self.pages[0].image
        return None

    def add_page(self, image: Image.Image, text: str = "") -> None:
        """Add a page to the book."""
        self.pages.append(BookPage(image=image, text=text, ocr_done=bool(text)))

    def remove_page(self, index: int) -> None:
        """Remove a page by index."""
        if 0 <= index < len(self.pages):
            self.pages.pop(index)
            if self.current_page >= len(self.pages) and self.pages:
                self.current_page = len(self.pages) - 1

    def move_page(self, from_idx: int, to_idx: int) -> None:
        """Move a page from one position to another."""
        if 0 <= from_idx < len(self.pages) and 0 <= to_idx < len(self.pages):
            page = self.pages.pop(from_idx)
            self.pages.insert(to_idx, page)

    def get_current_page(self) -> BookPage | None:
        """Get the current page."""
        if 0 <= self.current_page < len(self.pages):
            return self.pages[self.current_page]
        return None

    def next_page(self) -> bool:
        """Move to next page. Returns True if moved, False if at end."""
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            return True
        return False

    def prev_page(self) -> bool:
        """Move to previous page. Returns True if moved, False if at start."""
        if self.current_page > 0:
            self.current_page -= 1
            return True
        return False

    def go_to_page(self, index: int) -> bool:
        """Go to a specific page. Returns True if valid."""
        if 0 <= index < len(self.pages):
            self.current_page = index
            return True
        return False


def get_image_thumbnail_base64(image: Image.Image, max_size: tuple[int, int] = (200, 200)) -> str:
    """Convert PIL Image to base64 thumbnail for display."""
    thumb = image.copy()
    thumb.thumbnail(max_size)
    buffer = io.BytesIO()
    thumb.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


def get_book_card_html(book: Book, index: int) -> str:
    """Generate HTML for a book card in the library view."""
    cover_b64 = ""
    if book.cover_image:
        cover_b64 = get_image_thumbnail_base64(book.cover_image, (150, 200))

    cover_html = (
        f'<img src="data:image/png;base64,{cover_b64}" style="max-height:150px; border-radius:8px;">'
        if cover_b64
        else '<div style="height:100px; background:#E0E0E0; border-radius:8px; display:flex; align-items:center; justify-content:center;">📖</div>'
    )

    return f"""
    <div class="book-card">
        {cover_html}
        <div class="title">{book.title}</div>
        <div class="meta">{book.page_count}페이지 | {book.created_at}</div>
    </div>
    """


def init_library(session_state) -> None:
    """Initialize book library in session state."""
    if "book_library" not in session_state:
        session_state.book_library = []
    if "current_book_index" not in session_state:
        session_state.current_book_index = None
    if "reading_history" not in session_state:
        session_state.reading_history = []


def add_book_to_library(session_state, book: Book) -> int:
    """Add a book to the library. Returns book index."""
    init_library(session_state)
    session_state.book_library.append(book)
    return len(session_state.book_library) - 1


def remove_book_from_library(session_state, index: int) -> None:
    """Remove a book from the library."""
    if 0 <= index < len(session_state.book_library):
        session_state.book_library.pop(index)
        if session_state.current_book_index == index:
            session_state.current_book_index = None
        elif session_state.current_book_index is not None and session_state.current_book_index > index:
            session_state.current_book_index -= 1


def add_to_reading_history(session_state, text: str, image: Image.Image | None = None) -> None:
    """Add an entry to reading history."""
    init_library(session_state)
    entry = {
        "time": datetime.datetime.now().strftime("%H:%M"),
        "text_preview": text[:80] + "..." if len(text) > 80 else text,
        "full_text": text,
        "image": image,
    }
    session_state.reading_history.insert(0, entry)
    # Keep max 20 entries
    if len(session_state.reading_history) > 20:
        session_state.reading_history = session_state.reading_history[:20]
