// Post.jsx
import React, { useState, useEffect } from "react";
import "../../styles/post.css";

const Post = ({
  post,
  onLike = null,
  onComment = null,
  onFollow = null, 
  isFollowing = false,
  currentUserId = null,
}) => {
  const isOwnPost = post.userId === currentUserId;
  const [followStatus, setFollowStatus] = useState(isFollowing);
  const imageUrl = post.image ? `http://localhost:5000/${post.image}` : null;

  useEffect(() => {
    
    setFollowStatus(isFollowing);
  }, [isFollowing]);

  const handleFollowClick = () => {
    setFollowStatus(!followStatus);
    onFollow(post.user_id);
  };

  return (
    <div className="post-card">
      <div className="post-header">
        <img
          src={`https://ui-avatars.com/api/?name=${post.username}&background=666&color=fff`}
          alt={post.username || ""}
          className="post-avatar"
        />

        <div className="post-user">
          <strong>{post.username || "Unknown User"}</strong>
        </div>

        {!isOwnPost && (
          <button
            className={`follow-btn ${followStatus ? "following" : ""}`}
            onClick={handleFollowClick}
          >
            {followStatus ? "✓ Following" : "+ Follow"}
          </button>
        )}
      </div>
      
      <div className="post-content">{post.text || "No content available"}</div>
      
      {imageUrl && (
        <div className="post-image-container">
          <img src={imageUrl}
            style={{ maxWidth: "100%", height: "auto" }}
            alt="Post"
            className="post-image"
          />
        </div>
      )}

      <div className="post-stats">
        <span className="post-stat">❤️ {post.like_count || 0} likes</span>
        <span className="post-stat">💬 {post.comment_count || 0} comments</span>
      </div>

      <div className="post-actions">
        <button className="action-btn" onClick={() => onLike(post.id)}>
          ❤️ Like
        </button>
        <button className="action-btn" onClick={() => onComment(post)}>
          💬 Comment
        </button>
        <span className="post-time">
          {new Date(post.date_of_post).toLocaleDateString("en-US", {
            month: "long",
            day: "numeric",
            year: "numeric",
          }) || "xy hours ago"}
        </span>
      </div>
    </div>
  );
};

export default Post;
