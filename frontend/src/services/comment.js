const API_BASE_URL = 'http://localhost:5000';


export const fetchCommentsByPostId = async (postId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/posts/${postId}/comments`, {
      credentials: 'include', 
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch comments');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching comments:', error);
    throw error;
  }
};

export const createComment = async (postId, text) => {
  try {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}/api/posts/${postId}/comments`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', 
      body: JSON.stringify({ text }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Failed to create comment');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error creating comment:', error);
    throw error;
  }
};

export const deleteComment = async (commentId) => {
  try {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}/api/comments/${commentId}`, {
      method: 'DELETE',
      credentials: 'include', 
    });
    
    if (!response.ok) {
      throw new Error('Failed to delete comment');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error deleting comment:', error);
    throw error;
  }
};