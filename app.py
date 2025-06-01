import streamlit as st
import os
from pathlib import Path
from ebook_search import EbookSearcher

# Page configuration
st.set_page_config(
    page_title="📚 Ebook Search System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        margin-bottom: 2rem;
    }
    .search-box {
        margin: 2rem 0;
    }
    .book-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #2E86AB;
    }
    .book-title {
        font-weight: bold;
        color: #2E86AB;
        font-size: 1.1rem;
    }
    .book-info {
        color: #666;
        font-size: 0.9rem;
    }
    .match-score {
        background-color: #28a745;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .directory-item {
        background-color: #f8f9fa;
        padding: 0.5rem;
        margin: 0.2rem 0;
        border-radius: 5px;
        border-left: 3px solid #2E86AB;
        color: #333;
        font-size: 0.9rem;
        word-wrap: break-word;
        word-break: break-all;
        white-space: normal;
        overflow-wrap: break-word;
    }
    .directory-item.invalid {
        border-left-color: #dc3545;
        color: #dc3545;
    }
</style>
""", unsafe_allow_html=True)

def initialize_directories():
    """Initialize the search directories in session state"""
    if 'search_directories' not in st.session_state:
        searcher = EbookSearcher()
        default_dirs = searcher.get_common_ebook_directories()
        st.session_state.search_directories = default_dirs.copy()

def main():
    # Initialize the searcher and directories
    if 'searcher' not in st.session_state:
        st.session_state.searcher = EbookSearcher()
    
    initialize_directories()
    
    # Title
    st.markdown("<h1 class='main-header'>📚 Ebook Search System</h1>", unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Search Configuration")
        
        # Search threshold
        similarity_threshold = st.slider(
            "Similarity Threshold",
            min_value=0,
            max_value=100,
            value=60,
            help="Minimum similarity score for search results"
        )
        
        st.markdown("---")
        
        # Directory Management Section
        st.subheader("📁 Search Directories Management")
        
        # Add new directory section
        st.markdown("**Add New Directory:**")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            new_directory = st.text_input(
                "Enter directory path:",
                placeholder="/path/to/your/ebooks",
                label_visibility="collapsed"
            )
        
        with col2:
            if st.button("Add", type="secondary"):
                if new_directory.strip() and new_directory not in st.session_state.search_directories:
                    if os.path.exists(new_directory):
                        st.session_state.search_directories.append(new_directory)
                        st.success("✅ Added!")
                        st.rerun()
                    else:
                        st.error("❌ Directory doesn't exist")
                elif new_directory in st.session_state.search_directories:
                    st.warning("⚠️ Already added")
        
        st.markdown("---")
        
        # Current directories section
        st.markdown("**Current Search Directories:**")
        
        if st.session_state.search_directories:
            # Quick actions
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Reset to Defaults", help="Restore default directories"):
                    searcher = st.session_state.searcher
                    st.session_state.search_directories = searcher.get_common_ebook_directories()
                    st.success("✅ Reset to defaults!")
                    st.rerun()
            
            with col2:
                if st.button("🗑️ Clear All", help="Remove all directories"):
                    st.session_state.search_directories = []
                    st.warning("⚠️ All directories cleared!")
                    st.rerun()
            
            st.markdown("**Active Directories:**")
            
            # Display each directory with remove option
            directories_to_remove = []
            
            for i, directory in enumerate(st.session_state.search_directories):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    # Check if directory exists and show status
                    if os.path.exists(directory):
                        st.markdown(f"""
                        <div class="directory-item">
                            ✅ {directory}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="directory-item invalid">
                            ❌ {directory}
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("🗑️", key=f"remove_{i}", help=f"Remove {directory}"):
                        directories_to_remove.append(directory)
            
            # Remove directories that were marked for removal
            for dir_to_remove in directories_to_remove:
                st.session_state.search_directories.remove(dir_to_remove)
                st.rerun()
                
        else:
            st.info("📭 No search directories configured. Add some directories above.")
        
        # Show summary
        valid_dirs = [d for d in st.session_state.search_directories if os.path.exists(d)]
        invalid_dirs = [d for d in st.session_state.search_directories if not os.path.exists(d)]
        
        st.markdown("---")
        st.markdown("**Summary:**")
        st.info(f"📂 **{len(valid_dirs)}** valid directories")
        if invalid_dirs:
            st.warning(f"⚠️ **{len(invalid_dirs)}** invalid directories")
    
    # Main search interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "🔍 Search for ebooks:",
            placeholder="Enter book title, author, or keywords...",
            key="search_input"
        )
    
    with col2:
        search_button = st.button("Search", type="primary", use_container_width=True)
    
    # Check if we have any valid directories before searching
    valid_search_directories = [d for d in st.session_state.search_directories if os.path.exists(d)]
    
    if not valid_search_directories:
        st.warning("⚠️ No valid search directories configured. Please add some directories in the sidebar.")
        return
    
    # Perform search when button is clicked or query changes
    if search_button or search_query:
        with st.spinner("🔍 Searching for ebooks..."):
            # Find all ebook files
            searcher = st.session_state.searcher
            all_books = searcher.find_ebook_files(valid_search_directories)
            
            if not all_books:
                st.warning("📭 No ebook files found in the specified directories.")
                st.info("Try adding more directories in the sidebar or check if you have ebooks in the configured locations.")
                return
            
            # Search for matching books
            if search_query.strip():
                results = searcher.search_books(search_query, all_books, similarity_threshold)
            else:
                results = [(book, 100) for book in all_books]
            
            # Display results
            st.subheader(f"📊 Search Results ({len(results)} found)")
            
            if not results:
                st.info("No books match your search criteria. Try lowering the similarity threshold or using different keywords.")
                return
            
            # Display search results
            for i, (book, score) in enumerate(results):
                with st.container():
                    col1, col2, col3 = st.columns([6, 2, 2])
                    
                    with col1:
                        st.markdown(f"""
                        <div class="book-card">
                            <div class="book-title">{book['filename']}</div>
                            <div class="book-info">
                                📁 {book['directory']}<br>
                                📏 {book['size_mb']} MB | 📄 {book['extension'].upper()}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div style="text-align: center; padding-top: 1rem;">
                            <span class="match-score">{score}% Match</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        if st.button(f"Open Folder", key=f"open_{i}"):
                            # Open file location in finder/explorer
                            import subprocess
                            import platform
                            
                            if platform.system() == "Darwin":  # macOS
                                subprocess.run(["open", "-R", book['full_path']])
                            elif platform.system() == "Windows":
                                subprocess.run(["explorer", "/select,", book['full_path']])
                            else:  # Linux
                                subprocess.run(["xdg-open", book['directory']])
    
    # Display statistics
    if 'all_books' in locals():
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📚 Total Books", len(all_books))
        
        with col2:
            total_size = sum(book['size_mb'] for book in all_books)
            st.metric("💾 Total Size", f"{total_size:.1f} MB")
        
        with col3:
            extensions = set(book['extension'] for book in all_books)
            st.metric("📄 File Types", len(extensions))
        
        with col4:
            directories = set(book['directory'] for book in all_books)
            st.metric("📁 Directories", len(directories))

if __name__ == "__main__":
    main() 