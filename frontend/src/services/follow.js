const BASE_URL = "http://localhost:5000/api/follow";

export const fetchFollowers = async (userId) => {
    const response = await fetch(`${BASE_URL}/${userId}/followers`, {
        method: 'GET',
        credentials: 'include',
    }
        
    );
    const data = await response.json();
    return data;
};

export const fetchFollowing = async (userId) => {
    const response = await fetch(`${BASE_URL}/${userId}/following`, {
        method: 'GET',
        credentials: 'include',
    });

    const data = await response.json();
    return data;
}


export const handleFollowUser = async (userId) => {
    const followRes = await followUser(userId);

    if (followRes.ok) {
        return { success: true,  action: 'followed' };
    }

    if (followRes.status === 409) {
        const unfollowRes = await unfollowUser(userId);
        return { success: unfollowRes.ok, action: 'unfollowed' };
    } 

    return { success: false, action: 'none' };
}


export const followUser = async (userId) => {
    try {
        const response = await fetch(`${BASE_URL}`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ following_id: userId }),
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Follow error:', response.status, errorText);
        }
        
        return response;
    } catch (error) {
        console.error('Network error:', error);
        return { ok: false, status: 500 };
    }
}

export const unfollowUser = async (userId) => {
    const response = await fetch(`${BASE_URL}/${userId}`, {
        method: 'DELETE',
        credentials: 'include',
    }); 
    return response;
}