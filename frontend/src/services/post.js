const BASE_URL = "http://localhost:5000/api/posts";



export const fetchPosts = async () => {
  const response = await fetch(BASE_URL, {
    credentials: 'include',
  });
  if (response.status === 401) {
    return { error: 'Unauthorized', code: 401 };
  }
  const data = await response.json();
  return data;
};

export const fetchLikedPosts = async () => {
  const response = await fetch(`${BASE_URL}/liked`, {
    credentials: 'include',
  });
  const data = await response.json();
  return data;
};

export const fetchRecommendedPosts = async (seenPostIds = []) => {
  const queryParams = new URLSearchParams();
  
  seenPostIds.forEach(id => queryParams.append('seen_ids', id));
  queryParams.append('limit', 10);

  const response = await fetch(`${BASE_URL}/recommendations?${queryParams.toString()}`, {
    credentials: 'include', 
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch recommendations');
  }

  const data = await response.json();
  return data;
};



export const createPost = async (text, imageFile) => {
  const formData = new FormData();
  
  formData.append('text', text);
  if (imageFile) formData.append('image_file', imageFile);  

  try {
    const response = await fetch(BASE_URL, {
      method: 'POST',
      body: formData,
      credentials: 'include', 
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.Message || 'Failed to create post');
    }

    const data = await response.json();
    return data;
  } catch (err) {
    throw err;
  }
};
