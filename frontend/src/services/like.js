const BASE_URL = "http://localhost:5000/api/posts";


export const HandleLikeLogicPost = async (postId, isCurrentlyLiked) => {
    try {
        if (isCurrentlyLiked) {
            const success = await unlikePost(postId);
            return { success: success, action: 'unliked' };
        } else {
            const status = await likePost(postId);
            
            const success = status === 200 || status === 201;
            return { success: success, action: 'liked' };
        }
    } catch (error) {
        console.error("Like logic error:", error);
        return { success: false, action: 'none' };
    }
};

export const likePost = async (postId) => {
    const response = await fetch(`${BASE_URL}/${postId}/like`, {
        method: "POST",
        credentials: "include",
    });

    return response.status;
};


export const unlikePost = async (postId) => {
    const response = await fetch(`${BASE_URL}/${postId}/like`, {
        method: "DELETE",
        credentials: "include",
    });
    return response.ok ? true : false;
};


