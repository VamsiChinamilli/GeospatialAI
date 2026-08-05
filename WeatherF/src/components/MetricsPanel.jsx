// src/components/MetricsPanel.jsx

import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from "recharts";

export default function MetricsPanel({
  metrics,
  activeBBox,
  locationDetails,
}) {
  // Common styling for grid background
  const gridBgStyle = {
    backgroundColor: "#f7f5ed",
    backgroundImage: `radial-gradient(#e2dfd2 1px, transparent 1px)`,
    backgroundSize: "20px 20px",
  };

  // Helper
  const formatNumber = (value, digits = 2) => {
    if (value === null || value === undefined) return "—";
    const number = Number(value);
    return Number.isNaN(number) ? "—" : number.toFixed(digits);
  };

  // ============================================================
  // Guard State
  // ============================================================
  if (!metrics) {
    return (
      <div
        style={{
          width: "100%",
          height: "100%",
          minHeight: "100vh",
          padding: "32px",
          boxSizing: "border-box",
          color: "#1c1917",
          fontFamily: "'Playfair Display', Georgia, serif",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          ...gridBgStyle,
        }}
      >
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "8px",
            padding: "6px 16px",
            borderRadius: "9999px",
            backgroundColor: "#e8ece6",
            border: "1px solid #d1d8cd",
            fontSize: "11px",
            fontFamily: "monospace",
            color: "#374151",
            marginBottom: "16px",
            letterSpacing: "0.05em",
          }}
        >
          <span
            style={{
              width: "6px",
              height: "6px",
              borderRadius: "50%",
              backgroundColor: "#10b981",
            }}
          />
          SYSTEM: STANDBY
        </div>

        <h1
          style={{
            margin: 0,
            fontSize: "32px",
            fontWeight: "700",
            letterSpacing: "0.02em",
            color: "#1c1917",
            textAlign: "center",
          }}
        >
          URBAN HEAT ISLAND
        </h1>
        <h2
          style={{
            margin: "4px 0 0 0",
            fontSize: "28px",
            fontStyle: "italic",
            fontWeight: "400",
            color: "#4a5d4e",
            textAlign: "center",
          }}
        >
          COPILOT ENGINE
        </h2>

        <p
          style={{
            marginTop: "16px",
            color: "#6b7280",
            fontFamily: "monospace",
            fontSize: "12px",
          }}
        >
          Waiting for urban climate telemetry analysis...
        </p>
      </div>
    );
  }

  // ============================================================
  // Data Extraction
  // ============================================================
  const landCover = metrics?.land_cover || {};
  const lst = metrics?.lst || {};

  const classPercentages = landCover?.class_percentages || {};
  const estimatedLst = lst?.estimated_lst_celsius ?? null;
  const expectedRange = lst?.expected_range_celsius || {};
  const classification = lst?.classification || "Unknown";
  const confidence = lst?.confidence ?? null;
  const dominantClass = landCover?.dominant_class || "Unknown";
  const totalEnvironmentalEffect = lst?.total_environmental_effect ?? null;
  const totalLandCoverEffect = lst?.total_land_cover_effect ?? null;
  const contributors = lst?.main_contributors || [];

  const landCoverData = Object.entries(classPercentages).map(([name, percentage]) => ({
    name,
    percentage: Number(percentage),
  }));

  return (
    <div
      style={{
        width: "100%",
        minHeight: "100vh",
        padding: "32px 24px",
        display: "flex",
        flexDirection: "column",
        gap: "24px",
        color: "#1c1917",
        boxSizing: "border-box",
        fontFamily: "'Playfair Display', Georgia, serif",
        ...gridBgStyle,
      }}
    >
      {/* ========================================================
          Header Section
      ======================================================== */}
      <div style={{ textAlign: "center", padding: "12px 0" }}>
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "8px",
            padding: "4px 14px",
            borderRadius: "9999px",
            backgroundColor: "#e2e8e0",
            border: "1px solid #c5d0c0",
            fontSize: "11px",
            fontFamily: "monospace",
            color: "#374151",
            letterSpacing: "0.08em",
            marginBottom: "12px",
          }}
        >
          <span
            style={{
              width: "6px",
              height: "6px",
              borderRadius: "50%",
              backgroundColor: "#2e6f40",
            }}
          />
          ENVIRONMENTAL STABILITY: NOMINAL
        </div>

        <h1
          style={{
            margin: 0,
            fontSize: "36px",
            fontWeight: "800",
            letterSpacing: "0.04em",
            color: "#1c1917",
            textTransform: "uppercase",
          }}
        >
          Urban Heat Island
        </h1>
        <h2
          style={{
            margin: "2px 0 0 0",
            fontSize: "32px",
            fontStyle: "italic",
            fontWeight: "400",
            color: "#3a5335",
            letterSpacing: "0.02em",
          }}
        >
          COPILOT ENGINE
        </h2>
      </div>

      {/* ========================================================
          Spatial Footprint Card
      ======================================================== */}
      <div
        style={{
          backgroundColor: "#ffffff",
          padding: "20px 24px",
          borderRadius: "16px",
          border: "1px solid #e5e7eb",
          boxShadow: "0 2px 10px rgba(0,0,0,0.03)",
          display: "flex",
          flexDirection: "column",
          gap: "12px",
        }}
      >
        <div>
          <span
            style={{
              color: "#6b7280",
              fontFamily: "monospace",
              fontSize: "10px",
              letterSpacing: "0.08em",
              display: "block",
            }}
          >
            TARGET CORE SECTOR REGION
          </span>
          <span
            style={{
              color: "#2d5a27",
              fontSize: "18px",
              fontWeight: "700",
              marginTop: "2px",
              display: "block",
            }}
          >
            {locationDetails || "Unknown Region"}
          </span>
        </div>

        <div style={{ borderTop: "1px solid #f3f4f6", paddingTop: "10px" }}>
          <span
            style={{
              color: "#6b7280",
              fontFamily: "monospace",
              fontSize: "10px",
              letterSpacing: "0.08em",
              display: "block",
              marginBottom: "2px",
            }}
          >
            CURRENT ACTIVE SPATIAL FOOTPRINT
          </span>
          <span
            style={{
              color: "#374151",
              fontFamily: "monospace",
              fontSize: "12px",
              fontWeight: "600",
            }}
          >
            {activeBBox ? `[${activeBBox.join(", ")}]` : "No footprint coordinates passed."}
          </span>
        </div>

        <div style={{ borderTop: "1px solid #f3f4f6", paddingTop: "10px" }}>
          <span
            style={{
              color: "#6b7280",
              fontFamily: "monospace",
              fontSize: "10px",
              letterSpacing: "0.08em",
              display: "block",
              marginBottom: "2px",
            }}
          >
            DOMINANT LAND COVER
          </span>
          <span style={{ color: "#1c1917", fontSize: "15px", fontWeight: "600" }}>
            {dominantClass}
          </span>
        </div>
      </div>

      {/* ========================================================
          Telemetry Grid (Key Metrics)
      ======================================================== */}
      <div style={{ display: "flex", gap: "16px", width: "100%", flexWrap: "wrap" }}>
        {/* Estimated LST */}
        <div
          style={{
            flex: 1,
            minWidth: "160px",
            backgroundColor: "#ffffff",
            padding: "20px",
            borderRadius: "16px",
            border: "1px solid #e5e7eb",
            boxShadow: "0 2px 10px rgba(0,0,0,0.03)",
          }}
        >
          <span
            style={{
              fontSize: "10px",
              fontWeight: "600",
              color: "#6b7280",
              fontFamily: "monospace",
              letterSpacing: "0.05em",
              display: "block",
            }}
          >
            ESTIMATED LST
          </span>
          <span
            style={{
              fontSize: "26px",
              fontWeight: "700",
              fontFamily: "monospace",
              color: "#1c1917",
              display: "block",
              marginTop: "8px",
            }}
          >
            {estimatedLst !== null ? `${formatNumber(estimatedLst)}°C` : "Calculating..."}
          </span>
        </div>

        {/* Thermal Classification */}
        <div
          style={{
            flex: 1,
            minWidth: "160px",
            backgroundColor: "#ffffff",
            padding: "20px",
            borderRadius: "16px",
            border: "1px solid #e5e7eb",
            boxShadow: "0 2px 10px rgba(0,0,0,0.03)",
          }}
        >
          <span
            style={{
              fontSize: "10px",
              fontWeight: "600",
              color: "#6b7280",
              fontFamily: "monospace",
              letterSpacing: "0.05em",
              display: "block",
            }}
          >
            THERMAL CLASSIFICATION
          </span>
          <span
            style={{
              fontSize: "24px",
              fontWeight: "700",
              fontFamily: "monospace",
              color: classification === "Hot" ? "#dc2626" : "#d97706",
              display: "block",
              marginTop: "8px",
            }}
          >
            {classification}
          </span>
        </div>

        {/* Confidence */}
        <div
          style={{
            flex: 1,
            minWidth: "160px",
            backgroundColor: "#ffffff",
            padding: "20px",
            borderRadius: "16px",
            border: "1px solid #e5e7eb",
            boxShadow: "0 2px 10px rgba(0,0,0,0.03)",
          }}
        >
          <span
            style={{
              fontSize: "10px",
              fontWeight: "600",
              color: "#6b7280",
              fontFamily: "monospace",
              letterSpacing: "0.05em",
              display: "block",
            }}
          >
            MODEL CONFIDENCE
          </span>
          <span
            style={{
              fontSize: "26px",
              fontWeight: "700",
              fontFamily: "monospace",
              color: "#2d5a27",
              display: "block",
              marginTop: "8px",
            }}
          >
            {confidence !== null ? `${formatNumber(confidence * 100, 0)}%` : "—"}
          </span>
        </div>
      </div>

      {/* ========================================================
          Expected Temperature Range
      ======================================================== */}
      <div
        style={{
          backgroundColor: "#ffffff",
          padding: "20px 24px",
          borderRadius: "16px",
          border: "1px solid #e5e7eb",
          boxShadow: "0 2px 10px rgba(0,0,0,0.03)",
        }}
      >
        <span
          style={{
            fontSize: "10px",
            fontWeight: "600",
            color: "#6b7280",
            fontFamily: "monospace",
            letterSpacing: "0.08em",
          }}
        >
          EXPECTED LAND SURFACE TEMPERATURE RANGE
        </span>

        <div style={{ display: "flex", gap: "40px", marginTop: "12px" }}>
          <div>
            <span style={{ color: "#9ca3af", fontSize: "11px", display: "block" }}>
              MINIMUM
            </span>
            <span
              style={{
                color: "#2563eb",
                fontSize: "22px",
                fontFamily: "monospace",
                fontWeight: "700",
              }}
            >
              {expectedRange.min !== undefined ? `${formatNumber(expectedRange.min)}°C` : "—"}
            </span>
          </div>

          <div>
            <span style={{ color: "#9ca3af", fontSize: "11px", display: "block" }}>
              MAXIMUM
            </span>
            <span
              style={{
                color: "#dc2626",
                fontSize: "22px",
                fontFamily: "monospace",
                fontWeight: "700",
              }}
            >
              {expectedRange.max !== undefined ? `${formatNumber(expectedRange.max)}°C` : "—"}
            </span>
          </div>
        </div>
      </div>

      {/* ========================================================
          U-Net Classification Output Chart
      ======================================================== */}
      <div
        style={{
          backgroundColor: "#ffffff",
          padding: "20px 24px",
          borderRadius: "16px",
          border: "1px solid #e5e7eb",
          boxShadow: "0 2px 10px rgba(0,0,0,0.03)",
          display: "flex",
          flexDirection: "column",
          gap: "12px",
          height: "320px",
          boxSizing: "border-box",
        }}
      >
        <span
          style={{
            fontSize: "10px",
            fontWeight: "600",
            color: "#6b7280",
            fontFamily: "monospace",
            letterSpacing: "0.08em",
          }}
        >
          U-NET PIXEL CLASSIFICATION OUTPUT (%)
        </span>

        <div style={{ width: "100%", flex: 1, minHeight: 0 }}>
          {landCoverData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={landCoverData}
                layout="vertical"
                margin={{ left: 10, right: 20, top: 10, bottom: 5 }}
              >
                <XAxis
                  type="number"
                  domain={[0, 100]}
                  stroke="#9ca3af"
                  fontSize={10}
                  tickLine={false}
                />
                <YAxis
                  dataKey="name"
                  type="category"
                  stroke="#4b5563"
                  fontSize={11}
                  width={120}
                  tickLine={false}
                />
                <Tooltip
                  formatter={(value) => `${Number(value).toFixed(2)}%`}
                  contentStyle={{
                    backgroundColor: "#ffffff",
                    borderColor: "#e5e7eb",
                    borderRadius: "8px",
                    boxShadow: "0 4px 12px rgba(0,0,0,0.05)",
                    color: "#1c1917",
                    fontFamily: "sans-serif",
                  }}
                />
                <Bar dataKey="percentage" radius={4} barSize={18}>
                  {landCoverData.map((entry, index) => {
                    let fill = "#4b5563";
                    const lower = entry.name.toLowerCase();

                    if (lower.includes("built")) fill = "#dc2626";
                    else if (lower.includes("tree") || lower.includes("vegetation")) fill = "#2d5a27";
                    else if (lower.includes("water")) fill = "#2563eb";
                    else if (lower.includes("crop")) fill = "#d97706";

                    return <Cell key={`cell-${index}`} fill={fill} />;
                  })}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div
              style={{
                color: "#9ca3af",
                fontFamily: "monospace",
                fontSize: "12px",
                display: "flex",
                height: "100%",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              No land-cover classification data available.
            </div>
          )}
        </div>
      </div>

      {/* ========================================================
          Thermal Contribution Analysis
      ======================================================== */}
      <div
        style={{
          backgroundColor: "#ffffff",
          padding: "20px 24px",
          borderRadius: "16px",
          border: "1px solid #e5e7eb",
          boxShadow: "0 2px 10px rgba(0,0,0,0.03)",
        }}
      >
        <span
          style={{
            fontSize: "10px",
            fontWeight: "600",
            color: "#6b7280",
            fontFamily: "monospace",
            letterSpacing: "0.08em",
          }}
        >
          THERMAL CONTRIBUTION ANALYSIS
        </span>

        <div style={{ display: "flex", gap: "16px", marginTop: "14px", flexWrap: "wrap" }}>
          <div
            style={{
              flex: 1,
              minWidth: "160px",
              padding: "14px",
              borderRadius: "12px",
              backgroundColor: "#f9fafb",
              border: "1px solid #f3f4f6",
            }}
          >
            <span style={{ display: "block", fontSize: "10px", color: "#6b7280", fontFamily: "monospace" }}>
              LAND-COVER EFFECT
            </span>
            <span
              style={{
                display: "block",
                marginTop: "4px",
                fontSize: "20px",
                fontFamily: "monospace",
                fontWeight: "700",
                color: totalLandCoverEffect >= 0 ? "#dc2626" : "#2d5a27",
              }}
            >
              {totalLandCoverEffect !== null ? `${formatNumber(totalLandCoverEffect)}°C` : "—"}
            </span>
          </div>

          <div
            style={{
              flex: 1,
              minWidth: "160px",
              padding: "14px",
              borderRadius: "12px",
              backgroundColor: "#f9fafb",
              border: "1px solid #f3f4f6",
            }}
          >
            <span style={{ display: "block", fontSize: "10px", color: "#6b7280", fontFamily: "monospace" }}>
              ENVIRONMENTAL EFFECT
            </span>
            <span
              style={{
                display: "block",
                marginTop: "4px",
                fontSize: "20px",
                fontFamily: "monospace",
                fontWeight: "700",
                color: totalEnvironmentalEffect >= 0 ? "#dc2626" : "#2d5a27",
              }}
            >
              {totalEnvironmentalEffect !== null ? `${formatNumber(totalEnvironmentalEffect)}°C` : "—"}
            </span>
          </div>
        </div>
      </div>

      {/* ========================================================
          Main Contributors List
      ======================================================== */}
      {contributors.length > 0 && (
        <div
          style={{
            backgroundColor: "#ffffff",
            padding: "20px 24px",
            borderRadius: "16px",
            border: "1px solid #e5e7eb",
            boxShadow: "0 2px 10px rgba(0,0,0,0.03)",
          }}
        >
          <span
            style={{
              fontSize: "10px",
              fontWeight: "600",
              color: "#6b7280",
              fontFamily: "monospace",
              letterSpacing: "0.08em",
            }}
          >
            MAIN THERMAL CONTRIBUTORS
          </span>

          <div
            style={{
              marginTop: "12px",
              display: "flex",
              flexDirection: "column",
              gap: "8px",
            }}
          >
            {contributors.map((contributor, index) => (
              <div
                key={`${contributor.class}-${index}`}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "12px 16px",
                  borderRadius: "10px",
                  backgroundColor: "#f9fafb",
                  border: "1px solid #f3f4f6",
                }}
              >
                <div>
                  <span style={{ fontSize: "14px", fontWeight: "600", color: "#1c1917" }}>
                    {contributor.class}
                  </span>
                  <span
                    style={{
                      display: "block",
                      marginTop: "2px",
                      fontSize: "10px",
                      color: contributor.direction === "warming" ? "#dc2626" : "#2d5a27",
                      textTransform: "uppercase",
                      fontFamily: "monospace",
                      fontWeight: "600",
                    }}
                  >
                    {contributor.direction}
                  </span>
                </div>

                <span
                  style={{
                    fontFamily: "monospace",
                    fontWeight: "700",
                    fontSize: "15px",
                    color: contributor.effect_celsius >= 0 ? "#dc2626" : "#2d5a27",
                  }}
                >
                  {contributor.effect_celsius >= 0 ? "+" : ""}
                  {formatNumber(contributor.effect_celsius)}°C
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}