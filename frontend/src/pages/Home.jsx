import React, {
  useEffect,
  useState,
  useMemo,
  useRef,
  useCallback,
} from "react";
import { useAuth } from "../hooks/useAuth";
import { useNavigate } from "react-router-dom";
import "../styles/index.css";
import "../styles/Home.css";
import {
  createPost,
  fetchPosts,
  fetchRecommendedPosts,
} from "../services/post";
import { fetchUsers } from "../services/user";
import CommentsModal from "../components/post/CommentsModal";
import Post from "../components/post/Post";
import { HandleLikeLogicPost } from "../services/like";
import {
  fetchFollowers,
  fetchFollowing,
  handleFollowUser,
} from "../services/follow";

const Home = () => {
  useEffect(() => {
    document.title = "Home - Content4You";
  }, []);

  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [users, setUsers] = useState([]);

  const [followers, setFollowers] = useState([]);
  const [following, setFollowing] = useState([]);

  const [feedPosts, setFeedPosts] = useState([]);

  // Explore tab posts
  const [explorePosts, setExplorePosts] = useState([]);
  const [hasMore, setHasMore] = useState(true);
  const [isFetching, setIsFetching] = useState(false);

  const isFetchingRef = useRef(false);
  const observerTarget = useRef(null);

  // new post refs
  const postInputRef = useRef(null);
  const fileInputRef = useRef(null);

  const [activeTab, setActiveTab] = useState("explore");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // states for comments modal
  const [selectedPost, setSelectedPost] = useState(null);
  const [showComments, setShowComments] = useState(false);

  

  const followingIds = useMemo(
    () => new Set(following.map((f) => f.user_id)),
    [following],
  );

  const suggestedUsers = useMemo(
    () =>
      users
        .filter((x) => x.id !== user.id 
                        && !followingIds.has(x.id))
        .slice(0, 2),
    [users, user.id, followingIds],
  );


  // Fetch followers and following
  useEffect(() => {
    const loadFollowData = async () => {
      try {
        const followersData = await fetchFollowers(user.id);
        setFollowers(followersData);
        const followingData = await fetchFollowing(user.id);
        setFollowing(followingData);

        user.followerCount = followersData.length;
        user.followingCount = followingData.length;
      } catch (err) {
        console.error("Failed to load follow data:", err);
      }
    };
    if (user) {
      loadFollowData();
    }
  }, [user, refreshTrigger]);


  // Fetch users for suggestions
  useEffect(() => {
    const users = async () => {
      try {
        const usersData = await fetchUsers();
        setUsers(usersData);
      } catch (err) {
        console.error("Failed to fetch users:", err);
      }
    };
    users();
  }, []);


  // explore post loader
  const loadMorePosts = useCallback(async () => {
    if (isFetchingRef.current || !hasMore) return;

    isFetchingRef.current = true;
    setIsFetching(true);

    try {
      const currentIds = explorePosts.map((p) => p.id);
      const newPosts = await fetchRecommendedPosts(currentIds);

      if (newPosts.length === 0) {
        setHasMore(false);
      } else {
        setExplorePosts((prev) => {
          const existingIds = new Set(prev.map((p) => p.id));
          const uniqueNewPosts = newPosts.filter((p) => !existingIds.has(p.id));
          return [...prev, ...uniqueNewPosts];
        });
      }
    } catch (err) {
      console.error("Error loading posts:", err);
    } finally {
      isFetchingRef.current = false;
      setIsFetching(false);
    }
  }, [explorePosts, hasMore]);


  // Infinite scroll observer
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          loadMorePosts();
        }
      },
      { threshold: 1.0 },
    );

    if (observerTarget.current) {
      observer.observe(observerTarget.current);
    }

    return () => {
      if (observerTarget.current) {
        observer.unobserve(observerTarget.current);
      }
    };
  }, [loadMorePosts]);


  useEffect(() => {
    const getFeedPosts = async () => {
      try {
        const postsData = await fetchPosts();

        if(postsData?.code === 401) {
          handleLogout();
          return;
        }

        const filteredFeedPosts = postsData.filter((post) =>
          followingIds.has(post.user_id),
        );
        setFeedPosts(filteredFeedPosts);
      } catch (err) {
        setError("Failed to load feed posts");
      }
    };
    getFeedPosts();
  }, [explorePosts, followingIds]);


  // handle logout
  const handleLogout = () => {
    logout();
    navigate("/auth");
  };


  // handle create post
  const handleCreatePost = async () => {
    const text = postInputRef.current.value;
    const file = fileInputRef.current.files[0];

    try {
      const result = await createPost(text, file);
      setRefreshTrigger(result.PostId);
      postInputRef.current.value = "";
      fileInputRef.current.value = "";
    } catch (error) {
      console.error("Error:", error.message);
    }
  };


  // Comment modal handlers
  const handleOpenComments = (post) => {
    const modalPost = {
      id: post.id,
      username: post.username,
      content: post.text,
      likes: post.likes || 0,
      comments: post.comments || 0,
      time: post.date_of_post || "xy hours ago",
    };
    setSelectedPost(modalPost);
    setShowComments(true);
  };


  const handleCloseComments = () => {
    setShowComments(false);
    setSelectedPost(null);
  };


  const handleFollow = async (userId) => {
    const followResult = await handleFollowUser(userId);
    setRefreshTrigger(refreshTrigger + 1);
  };


  const handleLike = async (postId) => {
    let postToUpdate = null;
    if (activeTab === "feed") {
      postToUpdate = feedPosts.find((p) => p.id === postId);
    } else {
      postToUpdate = explorePosts.find((p) => p.id === postId);
    }

    if (!postToUpdate) return;

    // post ID + liked
    const likeResult = await HandleLikeLogicPost(postId, postToUpdate.is_liked);

    if (likeResult.success) {
      const updatedPosts = explorePosts.map((post) => {
        if (post.id === postId) {
          const countChange = likeResult.action === "liked" ? 1 : -1;
          return {
            ...post,
            like_count: Math.max(0, (post.like_count || 0) + countChange),
            is_liked: likeResult.action === "liked",
          };
        }
        return post;
      });

      setExplorePosts(updatedPosts);
    }
  };


  const getAvatarColor = (id) => {
    const colors = ["4CAF50", "2196F3", "FF5722", "9C27B0", "FF9800", "00BCD4"];
    return colors[id % colors.length];
  };


  return (
    <>
      <div className="home-container">
        {/* Navbar */}
        <nav className="navbar">
          <div className="nav-brand">Content4You</div>
          <div className="nav-tabs">
            <button
              className={`tab-button ${
                activeTab === "explore" ? "active" : ""
              }`}
              onClick={() => setActiveTab("explore")}
            >
              Explore
            </button>
            <button
              className={`tab-button ${activeTab === "feed" ? "active" : ""}`}
              onClick={() => setActiveTab("feed")}
            >
              Feed
            </button>
          </div>
          <div className="nav-actions">
            <button
              className="profile-btn"
              onClick={() => navigate("/profile")}
            >
              Profile
            </button>
            <button className="logout-btn" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </nav>

        <div className="home-content">
          {/* Main Feed */}
          <div className="feed-section">
            <div className="welcome-header">
              <h1>Welcome back, {user?.username}! 👋</h1>
            </div>

            {/* Create Post */}
            <div className="create-post">
              <div className="post-input-container">
                <img
                  src={`https://ui-avatars.com/api/?name=${user?.username}&background=4CAF50&color=fff`}
                  alt="Profile"
                  className="user-avatar"
                />
                <input
                  ref={postInputRef}
                  type="text"
                  placeholder="What's on your mind?"
                  className="post-input"
                />
                <label className="file-upload">
                  <input
                    ref={fileInputRef}
                    type="file"
                    className="post-file-input"
                    required
                  />
                  <span className="file-icon"></span>
                  <span className="checkmark"></span>
                </label>
              </div>
              <button className="post-button" onClick={handleCreatePost}>
                Post
              </button>
            </div>

            {/* Posts Feed */}
            <div className="posts-container">
              {(activeTab === "feed" ? feedPosts : explorePosts).map((post) => (
                <Post
                  key={post.id}
                  post={post}
                  onLike={handleLike}
                  onComment={handleOpenComments}
                  onFollow={handleFollow}
                  isFollowing={followingIds.has(post.user_id)}
                  currentUserId={user.id}
                />                
              ))}
              {activeTab === "feed" && feedPosts.length === 0 && (
                <p className="no-posts-message">
                  Your feed is empty. Follow some users to see their posts!
                </p>
              )}

              {/* Loading trigger for infinite scroll */}
              {activeTab === "explore" && (
                <div
                  ref={observerTarget}
                  className="loading-trigger"
                  style={{
                    height: "20px",
                    margin: "20px 0",
                    textAlign: "center",
                  }}
                >
                  {isFetching && <p>Loading more recommendations...</p>}
                  {!hasMore && explorePosts.length > 0 && (
                    <p>You've seen it all! 🎉</p>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Right Profile Sidebar */}
          <div className="profile-sidebar">
            <div className="profile-card">
              <img
                src={`https://ui-avatars.com/api/?name=${user?.username}&background=4CAF50&color=fff&size=80`}
                alt="Profile"
                className="profile-avatar"
              />
              <h3>{user?.username}</h3>
              <p className="profile-email">{user?.email}</p>
              <div className="profile-stats">
                <div className="stat">
                  <strong>
                    {
                      explorePosts.filter(
                        (post) => post.username === user.username,
                      ).length
                    }
                  </strong>
                  <span>Posts</span>
                </div>
                <div className="stat">
                  <strong>{followers.length}</strong>
                  <span>Followers</span>
                </div>
                <div className="stat">
                  <strong>{following.length}</strong>
                  <span>Following</span>
                </div>
              </div>
              <button
                className="edit-profile-btn"
                onClick={() => navigate("/profile")}
              >
                Edit Profile
              </button>
            </div>

            {/* Suggestions */}
            <div className="suggestions-card">
              <h4>Suggestions for You</h4>
              {suggestedUsers
                .map((suggestedUser, index) => (
                  <div key={index} className="suggestion-item">
                    <img
                      src={`https://ui-avatars.com/api/?name=${
                        suggestedUser.username
                      }&background=${getAvatarColor(suggestedUser.id)}&color=fff`}
                      alt={suggestedUser.username}
                      className="suggestion-avatar"
                    />
                    <div className="suggestion-info">
                      <strong>{suggestedUser.username}</strong>
                      <span>Suggested for you</span>
                    </div>
                    <button
                      className="follow-btn"
                      onClick={() => handleFollow(suggestedUser.id)}
                    >
                      Follow
                    </button>
                  </div>
                ))}
            </div>
          </div>
        </div>
      </div>
      {/* Comments Modal */}
      {showComments && selectedPost && (
        <CommentsModal
          post={selectedPost}
          onClose={handleCloseComments}
          trigger={setRefreshTrigger}
        />
      )}
    </>
  );
};

export default Home;
