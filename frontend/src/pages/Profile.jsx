import React, { useEffect, useState } from "react";
import { useAuth } from "../hooks/useAuth";
import { useNavigate } from "react-router-dom";
import { fetchPosts, fetchLikedPosts } from "../services/post";
import { fetchUserStatistics } from "../services/user";
import { HandleLikeLogicPost } from "../services/like";
import Post from "../components/post/Post";
import "../styles/index.css";
import "../styles/Profile.css";
import {
  fetchFollowers,
  fetchFollowing,
  handleFollowUser,
} from "../services/follow";
import {
  PieChart,
  Pie,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Cell,
} from "recharts";

const Profile = () => {
  useEffect(() => {
    document.title = "Profile - Content4You";
  }, []);

  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState("own-posts");

  const [isEditing, setIsEditing] = useState(false);

  const [userPosts, setUserPosts] = useState([]);
  const [likedPosts, setLikedPosts] = useState([]);
  const [statistics, setStatistics] = useState([]);

  const [followers, setFollowers] = useState([]);
  const [following, setFollowing] = useState([]);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [profileData, setProfileData] = useState({
    username: user?.username || "",
    email: user?.email || "",
    bio: "test bio",
    location: "test location",
    joinedDate: new Date(user?.dateOfCreate).toLocaleDateString("en-US", {
      month: "long",
      day: "numeric",
      year: "numeric",
    }),
  });

  const handleSave = () => {
    setIsEditing(false);
  };

  const handleChange = (e) => {
    setProfileData({
      ...profileData,
      [e.target.name]: e.target.value,
    });
  };

  const handleLogout = () => {
    logout();
    navigate("/auth");
  };

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
  }, [refreshTrigger]);

  useEffect(() => {
    const loadPosts = async () => {
      setLoading(true);
      try {
        const postsData = await fetchPosts();
        const userSpecificPosts = postsData.filter(
          (post) => post.username === user.username,
        );
        setUserPosts(userSpecificPosts);
      } catch (err) {
        setError("Failed to load posts");
      }
      setLoading(false);
    };
    loadPosts();

    const loadLikedPosts = async () => {
      setLoading(true);
      try {
        const postsData = await fetchLikedPosts();
        setLikedPosts(postsData);
      } catch (err) {
        setError("Failed to load liked posts");
      }
      setLoading(false);
    };
    loadLikedPosts();

    const loadStatistics = async () => {
      setLoading(true);
      try {
        const statsData = await fetchUserStatistics(user.id);
        setStatistics(statsData);
      } catch (err) {
        setError("Failed to load statistics");
      }
      setLoading(false);
    };
    loadStatistics();
  }, [refreshTrigger]);

  const handleLike = async (postId) => {
    let postToUpdate = likedPosts.find((p) => p.id === postId);
    if (!postToUpdate) return;

    const likeResult = await HandleLikeLogicPost(postId, postToUpdate.is_liked);

    if (likeResult.success) {
      const updatedPosts = likedPosts.map((post) => {
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

      setLikedPosts(updatedPosts);
      setRefreshTrigger(refreshTrigger + 1);
    }
  };

  const handleComment = (postId) => {
    console.log(`Commented on post ${postId}`);
  };

  const handleFollow = async (userId) => {
    const followResult = await handleFollowUser(userId);
    setRefreshTrigger(refreshTrigger + 1);
  };

  const getActiveTab = (activeTab) => {
    switch (activeTab) {
      case "own-posts":
        return userPosts;
      case "liked-posts":
        return likedPosts;
      case "statistics":
        return statistics;
      default:
        return [];
    }
  };

  const chartData = Object.entries(statistics).map(([tag, interactions]) => ({
    tag,
    interactions,
  }));

  const COLORS = [
    "#00549d",
    "#00967a",
    "#a87403",
    "#a73801",
    "#65039a",
    "#a60019",
    "#008a5c",
    "#2600a4",
    "#9b034f",
    "#9c8609",
    "#FF6347",
    "#a20306",
  ];
  return (
    <div className="profile-container">
      {/* Navigation */}
      <nav className="profile-nav">
        <button className="back-button" onClick={() => navigate("/")}>
          ← Back
        </button>
        <h2 className="nav-title">Profile</h2>
        <div className="nav-actions">
          <button
            className={`edit-profile-btn ${isEditing ? "editing" : ""}`}
            onClick={() => setIsEditing(!isEditing)}
          >
            {isEditing ? "Cancel" : "Edit"}
          </button>
        </div>
      </nav>

      <div className="profile-content">
        {/* Profile Header */}
        <div className="profile-header">
          <div className="cover-container">
            <div className="cover-photo">
              <div className="cover-overlay"></div>
            </div>
            <div className="profile-avatar-section">
              <img
                src={`https://ui-avatars.com/api/?name=${user?.username}  &background=4CAF50&color=fff&size=120&bold=true`}
                alt="Profile"
                className="profile-avatar"
              />
            </div>
          </div>

          <div className="profile-info">
            <div className="profile-main">
              <div className="profile-text">
                {isEditing ? (
                  <input
                    type="text"
                    name="username"
                    value={profileData.username}
                    onChange={handleChange}
                    className="edit-input username-input"
                    placeholder="Username"
                  />
                ) : (
                  <h1 className="profile-name">{profileData.username}</h1>
                )}

                <div className="profile-bio">
                  {isEditing ? (
                    <textarea
                      name="bio"
                      value={profileData.bio}
                      onChange={handleChange}
                      className="edit-textarea"
                      placeholder="Tell us about yourself..."
                      rows="2"
                    />
                  ) : (
                    <p>{profileData.bio}</p>
                  )}
                </div>

                <div className="profile-meta">
                  {isEditing ? (
                    <div className="edit-meta">
                      <input
                        type="text"
                        name="location"
                        value={profileData.location}
                        onChange={handleChange}
                        className="edit-input"
                        placeholder="Location"
                      />
                    </div>
                  ) : (
                    <>
                      <div className="meta-item">
                        <span className="meta-icon">📍</span>
                        <span>{profileData.location}</span>
                      </div>
                      <div className="meta-item">
                        <span className="meta-icon">📅</span>
                        <span>{profileData.joinedDate}</span>
                      </div>
                    </>
                  )}
                </div>
              </div>

              <div className="profile-stats">
                <div className="stat-item">
                  <div className="stat-number">{userPosts.length}</div>
                  <div className="stat-label">Posts</div>
                </div>
                <div className="stat-item">
                  <div className="stat-number">{followers.length}</div>
                  <div className="stat-label">Followers</div>
                </div>
                <div className="stat-item">
                  <div className="stat-number">{following.length}</div>
                  <div className="stat-label">Following</div>
                </div>
              </div>
            </div>

            {isEditing && (
              <button className="save-profile-btn" onClick={handleSave}>
                Save Changes
              </button>
            )}
          </div>
        </div>

        {/* Posts Section */}
        <div className="posts-section">
          <div className="nav-tabs">
            <button
              className={`tab-button ${
                activeTab === "own-posts" ? "active" : ""
              }`}
              onClick={() => setActiveTab("own-posts")}
            >
              Own posts
            </button>
            <button
              className={`tab-button ${activeTab === "liked-posts" ? "active" : ""}`}
              onClick={() => setActiveTab("liked-posts")}
            >
              Liked Posts
            </button>
            <button
              className={`tab-button ${
                activeTab === "statistics" ? "active" : ""
              }`}
              onClick={() => setActiveTab("statistics")}
            >
              Statistics
            </button>
          </div>

          <div className="posts-grid">
            {activeTab === "statistics" ? (
              <div className="statistics-chart">
                <div className="pie-chart ">
                  <PieChart width={700} height={700}>
                    <Pie
                      data={chartData}
                      dataKey="interactions"
                      nameKey="tag"
                      innerRadius={60}
                    >
                      {chartData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS[index % COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </div>
                <div className="bar-chart">
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="tag" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="interactions">
                        {chartData.map((entry, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={COLORS[index % COLORS.length]}
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            ) : (
              getActiveTab(activeTab).map((data) => (
                <Post
                  key={data.id}
                  post={data}
                  onLike={handleLike}
                  onComment={handleComment}
                  onFollow={handleFollow}
                  currentUserId={user.id}
                />
              ))
            )}
          </div>

          {userPosts.length === 0 && activeTab === "own-posts" && (
            <div className="empty-posts">
              <div className="empty-icon">📝</div>
              <h4>No posts yet</h4>
              <p>Share your thoughts with the community</p>
              <button className="create-post-btn">Create first post</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;
