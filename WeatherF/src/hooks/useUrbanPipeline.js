
// src/hooks/useUrbanPipeline.js

import { useEffect, useRef, useState } from "react";

const API_BASE_URL = "http://127.0.0.1:8000/";
const WS_BASE_URL = "ws://127.0.0.1:8000/ws/chat/";
const LOCATION_STORAGE_KEY = "urban_location_";

export function useUrbanPipeline({
  bboxQuery,
  sessionQuery,
}) {
  // ============================================================
  // BBOX
  // ============================================================

  const bboxValues = bboxQuery
    ? bboxQuery.split(",").map(Number)
    : null;

  /*
    Frontend/map format:

      [minLng, minLat, maxLng, maxLat]

    Example:

      [
        78.9532,
        20.5755,
        79.0078,
        20.6183
      ]

    Backend REST endpoint expects exactly this array.
  */

  const bbox =
    bboxValues && bboxValues.length === 4
      ? {
          min_lat: bboxValues[1],
          min_lon: bboxValues[0],
          max_lat: bboxValues[3],
          max_lon: bboxValues[2],
        }
      : null;

  // ============================================================
  // State
  // ============================================================

  const [metrics, setMetrics] = useState(null);
  const [activeBBox, setActiveBBox] = useState(bboxValues);
  const [conversation, setConversation] = useState([]);

  const [sessionId, setSessionId] = useState(null);

  const [statusMessage, setStatusMessage] = useState(
    "Preparing urban climate analysis..."
  );

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);

  const [locationDetails, setLocationDetails] = useState(
    "Fetching region details..."
  );

  // ============================================================
  // Refs
  // ============================================================

  const socketRef = useRef(null);
  const analysisStartedForBBoxRef = useRef(null);

  // ============================================================
  // Phase 1
  // REST analysis
  // ============================================================
// ============================================================
// Load existing session (stateful refresh support)
// ============================================================

useEffect(() => {
  if (!sessionQuery) {
    return;
  }

  async function loadExistingSession() {
    try {
      setStatusMessage("Loading saved analysis...");

      const response = await fetch(
        `${API_BASE_URL}/api/chat/${sessionQuery}/`
);

      if (!response.ok) {
        throw new Error("Failed to load saved session");
      }

      const session = await response.json();

      console.log("📂 Loaded existing session:", session);

setSessionId(session.id);

if (session.messages) {
  setConversation(session.messages);
}

// --------------------------------------------------------
// Restore analysis without rerunning the models
// --------------------------------------------------------

if (session.analysis) {
  setMetrics(session.analysis.analysis_metrics);
  setActiveBBox(session.analysis.bbox);
}

// --------------------------------------------------------
// Restore location details
// --------------------------------------------------------

const savedLocation = localStorage.getItem(
  `${LOCATION_STORAGE_KEY}${session.id}`
);

if (savedLocation) {

  console.log(
    "📍 Restored saved location:",
    savedLocation
  );

  setLocationDetails(savedLocation);

} else {

  console.log(
    "📍 No saved location found — reverse geocoding restored BBox..."
  );

  const restoredBBox = session.analysis?.bbox;

  if (restoredBBox) {
    fetchReverseGeocode(restoredBBox);
  }
}

setStatusMessage("");
    } catch (error) {
      console.error("❌ Failed to load session:", error);

      setStatusMessage(
        "Failed to load saved analysis."
      );
    }
  }

  loadExistingSession();
}, [sessionQuery]);

// ============================================================
// Phase 1
// REST analysis
// ============================================================


// ============================================================
// Reverse Geocoding
// ============================================================

async function fetchReverseGeocode(targetBBox, targetSessionId = null) {
  if (!targetBBox || targetBBox.length !== 4) {
    return;
  }

  try {

    const [minLng, minLat, maxLng, maxLat] = targetBBox;

    const centerLng =
      (minLng + maxLng) / 2;

    const centerLat =
      (minLat + maxLat) / 2;

    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${centerLat}&lon=${centerLng}&zoom=10`
    );

    if (!response.ok) {
      throw new Error(
        `Reverse geocoding failed: ${response.status}`
      );
    }

    const data = await response.json();

    if (data?.address) {

      const city =
        data.address.city ||
        data.address.town ||
        data.address.village ||
        "";

      const district =
        data.address.county ||
        data.address.district ||
        "";

      const state =
        data.address.state ||
        "";

      const location = [
        city,
        district,
        state,
      ]
        .filter(Boolean)
        .join(", ") || "Unknown Region";

      console.log(
        "📍 Reverse geocoded location:",
        location
      );

      setLocationDetails(location);

      // ------------------------------------------------------
      // Persist location for this specific session
      // ------------------------------------------------------

      if (targetSessionId) {

        localStorage.setItem(
          `${LOCATION_STORAGE_KEY}${targetSessionId}`,
          location
        );

        console.log(
          "💾 Saved location for session:",
          targetSessionId
        );
      }

      return location;
    }

  } catch (error) {

    console.warn(
      "⚠️ Reverse geocoding failed:",
      error
    );

    setLocationDetails(
      "Region Matrix Footprint"
    );
  }
}



useEffect(() => {
  // If a saved session exists, do NOT rerun analysis
  if (sessionQuery) {
    return;
  }

  if (!bbox || !bboxQuery) {
    return;
  }

  // Prevent duplicate requests for the same BBox
  if (analysisStartedForBBoxRef.current === bboxQuery) {
    return;
  }

  analysisStartedForBBoxRef.current = bboxQuery;

  async function runAnalysis() {
    try {
      setIsAnalyzing(true);
      setStatusMessage("Running urban climate analysis...");

      console.log("🚀 Starting analysis:", bbox);

      const response = await fetch(
        `${API_BASE_URL}/api/analyze/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            bbox: bboxValues,
          }),
        }
      );

      if (!response.ok) {
        const errorText = await response.text();

        throw new Error(
          `Analysis request failed (${response.status}): ${errorText}`
        );
      }

      const result = await response.json();

      console.log("📊 Analysis response:", result);

      // --------------------------------------------------------
      // Extract actual analysis metrics
      // --------------------------------------------------------

      const analysisMetrics =
        result.analysis?.analysis_metrics ||
        result.metrics ||
        result.analysis ||
        result;

      console.log(
        "📈 Analysis metrics:",
        analysisMetrics
      );

      setMetrics(analysisMetrics);

      // --------------------------------------------------------
      // Backend canonical BBox
      // --------------------------------------------------------

      const returnedBBox =
        result.analysis?.bbox ||
        analysisMetrics?.bbox ||
        bboxValues;

      setActiveBBox(returnedBBox);

      // --------------------------------------------------------
      // Extract ConversationSession ID
      // --------------------------------------------------------

      const newSessionId =
        result.session?.id ||
        result.session_id;

      console.log("🔎 Session extraction:", {
        resultSession: result.session,
        resultSessionId: result.session_id,
        extractedSessionId: newSessionId,
      });

      if (!newSessionId) {
        throw new Error(
          "Analysis succeeded but no conversation session ID was returned."
        );
      }

      console.log(
        "🆔 Conversation session:",
        newSessionId
      );

      // IMPORTANT:
      // This state update triggers the WebSocket effect.
      console.log(
        "➡️ Setting sessionId state:",
        newSessionId
      );

      setSessionId(newSessionId);

// Make dashboard stateful
window.history.replaceState(
  {},
  "",
  `/dashboard?session=${newSessionId}`
);

setStatusMessage("");

      // --------------------------------------------------------
      // Reverse geocoding
      // --------------------------------------------------------

      fetchReverseGeocode(returnedBBox,
  newSessionId);

    } catch (error) {
      console.error(
        "❌ Urban analysis failed:",
        error
      );

      setStatusMessage(
        `Error: ${error.message}`
      );

    } finally {
      setIsAnalyzing(false);
    }
  }



  runAnalysis();

}, [bboxQuery, sessionQuery]);



  // ============================================================
  // Phase 2
  // Conversation WebSocket
  // ============================================================

useEffect(() => {
  console.log("🔄 WebSocket effect triggered");
  console.log("🆔 Current sessionId:", sessionId);

  if (!sessionId) {
    console.log("⏸️ No sessionId yet — WebSocket not starting");
    return;
  }

  console.log("🔌 Connecting to conversation WebSocket...");

  const wsUrl = `${WS_BASE_URL}/ws/chat/${sessionId}/`;

  console.log("🌐 WebSocket URL:", wsUrl);

  const ws = new WebSocket(wsUrl);

  socketRef.current = ws;

  ws.onopen = () => {
    console.log("🟢 Conversation WebSocket connected");
    console.log("🆔 Session:", sessionId);
  };

  ws.onmessage = (event) => {
    try {
      const payload = JSON.parse(event.data);

      console.log("📥 WebSocket:", payload);

      switch (payload.type) {
        case "connection":
          console.log(
            "✅ Session connected:",
            payload.session_id
          );
          break;

        case "response_start":
          setIsStreaming(true);

          setConversation((previous) => [
            ...previous,
            {
              role: "assistant",
              content: "",
            },
          ]);

          break;

        case "token":
          setIsStreaming(true);

          setConversation((previous) => {
            if (previous.length === 0) {
              return [
                {
                  role: "assistant",
                  content: payload.content || "",
                },
              ];
            }

            const updated = [...previous];

            const last = updated[updated.length - 1];

            if (last?.role === "assistant") {
              updated[updated.length - 1] = {
                ...last,
                content:
                  last.content +
                  (payload.content || ""),
              };
            }

            return updated;
          });

          break;

        case "response_end":
          setIsStreaming(false);
          break;

        case "error":
          console.error(
            "❌ Backend error:",
            payload.message
          );

          setIsStreaming(false);

          setStatusMessage(
            `Error: ${payload.message}`
          );

          break;

        default:
          console.log(
            "ℹ️ Unknown WebSocket event:",
            payload
          );
      }
    } catch (error) {
      console.error(
        "❌ WebSocket JSON parsing error:",
        error
      );
    }
  };

  ws.onerror = (error) => {
    console.error("🔴 WebSocket error:", error);
  };

  ws.onclose = (event) => {
    console.log(
      "🔴 WebSocket closed:",
      event.code,
      event.reason
    );

    socketRef.current = null;
    setIsStreaming(false);
  };

  return () => {
    console.log(
      "🧹 Cleaning up conversation WebSocket..."
    );

    if (
      ws.readyState === WebSocket.OPEN ||
      ws.readyState === WebSocket.CONNECTING
    ) {
      ws.close();
    }

    socketRef.current = null;
  };
}, [sessionId]);

  // ============================================================
  // Send chat message
  // ============================================================

  const handleSendMessage = (messageText) => {
    const message = messageText.trim();

    if (!message) {
      return;
    }

    const socket = socketRef.current;

    if (
      !socket ||
      socket.readyState !== WebSocket.OPEN
    ) {
      console.error(
        "❌ WebSocket is not connected."
      );

      setStatusMessage(
        "Chat connection is not available."
      );

      return;
    }

    // ----------------------------------------------------------
    // Show user message immediately
    // ----------------------------------------------------------

    setConversation((previous) => [
      ...previous,
      {
        role: "user",
        content: message,
      },
    ]);

    // ----------------------------------------------------------
    // Current backend protocol
    // ----------------------------------------------------------

    socket.send(
      JSON.stringify({
        message,
      })
    );

    console.log(
      "📤 Chat message sent:",
      message
    );
  };

  // ============================================================
  // Return
  // ============================================================

  return {
    metrics,
    activeBBox,
    statusMessage,
    conversation,
    isStreaming,
    isAnalyzing,
    locationDetails,
    sessionId,
    handleSendMessage,
  };
}
