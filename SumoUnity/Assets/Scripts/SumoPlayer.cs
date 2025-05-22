using System.Collections.Generic;
using UnityEngine;
using TMPro;
using UnityEngine.UI;

public class SumoPlayer : MonoBehaviour
{
    [Tooltip("Prefab used to instantiate vehicles")]
    public GameObject vehiclePrefab;

    [Tooltip("Materials for priorities 1 to 5 (index 0 = priority 1)")]
    public Material[] priorityMaterials = new Material[5];

    [Tooltip("Vertical offset to adjust vehicle height on the lane")]
    public float verticalOffset = 0.6f;

    [Tooltip("Vertical offset to position the popup above the vehicle")]
    public float popupVerticalOffset = 2.0f;

    private Dictionary<string, GameObject> vehicleObjects = new();
    private Dictionary<string, TextMeshProUGUI> vehiclePopups = new();

    private SumoReceiver receiver;
    private SUMONetworkVisualizer networkVisualizer;
    // Tracks previous tile positions of each vehicle
    private Dictionary<string, Vector2Int> previousVehicleTiles = new();


    private bool cameraTargetSet = false;

    void Start()
    {
        receiver = FindObjectOfType<SumoReceiver>();
        if (receiver == null)
        {
            Debug.LogError("SumoReceiver not found in scene.");
        }
        networkVisualizer = FindObjectOfType<SUMONetworkVisualizer>();
        if (networkVisualizer == null)
        {
            Debug.LogWarning("SUMONetworkVisualizer not found in scene. Pollution tiles will not update.");
        }
    }

    void Update()
    {
        if (receiver == null) return;

        Dictionary<string, VehicleData> snapshot;

        lock (receiver.vehicleLock)
        {
            snapshot = new Dictionary<string, VehicleData>(receiver.liveVehicles); // use copy to avoid lock in Update
        }
        if (networkVisualizer != null)
        {
            Dictionary<Vector2Int, PollutionLevels> tilePollutionChanges = new();

            foreach (var kvp in snapshot)
            {
                string vehicleID = kvp.Key;
                var state = kvp.Value;

                Vector3 vehiclePos = new Vector3(state.x, 0, state.y);

                int tileX = Mathf.FloorToInt((vehiclePos.x - networkVisualizer.MinX) / networkVisualizer.pollutionTileSize);
                int tileZ = Mathf.FloorToInt((vehiclePos.z - networkVisualizer.MinZ) / networkVisualizer.pollutionTileSize);
                Vector2Int currentTile = new(tileX, tileZ);

                // Extract pollution levels from vehicle state
                PollutionLevels pollution = new PollutionLevels
                {
                    CO2 = state.CO2,
                    CO = state.CO,
                    HC = state.HC,
                    NOx = state.NOx,
                    PMx = state.PMx
                };

                if (previousVehicleTiles.TryGetValue(vehicleID, out Vector2Int previousTile))
                {
                    if (previousTile != currentTile)
                    {
                        // Subtract from old tile
                        if (!tilePollutionChanges.ContainsKey(previousTile))
                            tilePollutionChanges[previousTile] = new PollutionLevels();

                        SubtractPollution(tilePollutionChanges[previousTile], pollution);

                        // Add to new tile
                        if (!tilePollutionChanges.ContainsKey(currentTile))
                            tilePollutionChanges[currentTile] = new PollutionLevels();

                        AddPollution(tilePollutionChanges[currentTile], pollution);

                        previousVehicleTiles[vehicleID] = currentTile;
                    }
                }
                else
                {
                    if (!tilePollutionChanges.ContainsKey(currentTile))
                        tilePollutionChanges[currentTile] = new PollutionLevels();

                    AddPollution(tilePollutionChanges[currentTile], pollution);

                    previousVehicleTiles[vehicleID] = currentTile;
                }
            }

            networkVisualizer.ApplyTilePollutionChanges(tilePollutionChanges);
        }

        foreach (var kvp in snapshot)
        {
            string id = kvp.Key;
            var state = kvp.Value;

            if (!vehicleObjects.ContainsKey(id))
            {
                var vehicleObj = Instantiate(vehiclePrefab);
                vehicleObj.name = $"Vehicle_{id}";
                vehicleObjects[id] = vehicleObj;

                int unclampedPriority = Mathf.Clamp((int)state.priority, 1, 5);
                Debug.Log($"Vehicle {id} has priority {unclampedPriority}");
                ApplyPriorityMaterial(vehicleObj, unclampedPriority);

                // --- Canvas-based popup UI ---
                GameObject canvasGO = new GameObject("PollutionPopupCanvas");
                canvasGO.transform.SetParent(vehicleObj.transform);
                canvasGO.transform.localPosition = new Vector3(0, popupVerticalOffset, 0);
                canvasGO.transform.localRotation = Quaternion.identity;
                canvasGO.layer = LayerMask.NameToLayer("UI");

                var canvas = canvasGO.AddComponent<Canvas>();
                canvas.renderMode = RenderMode.WorldSpace;
                canvas.scaleFactor = 10f;
                canvas.sortingOrder = 100;

                canvasGO.AddComponent<CanvasScaler>();
                canvasGO.AddComponent<GraphicRaycaster>();
                canvasGO.AddComponent<FaceCamera>();

                RectTransform canvasRect = canvas.GetComponent<RectTransform>();
                canvasRect.sizeDelta = new Vector2(300, 180);
                canvasRect.localScale = Vector3.one * 0.01f;

                GameObject bgGO = new GameObject("Background");
                bgGO.transform.SetParent(canvasGO.transform, false);
                var bgImage = bgGO.AddComponent<Image>();
                bgImage.color = new Color(0f, 0f, 0f, 0.5f);
                RectTransform bgRect = bgImage.GetComponent<RectTransform>();
                bgRect.anchorMin = Vector2.zero;
                bgRect.anchorMax = Vector2.one;
                bgRect.offsetMin = Vector2.zero;
                bgRect.offsetMax = Vector2.zero;

                GameObject textGO = new GameObject("PollutionText");
                textGO.transform.SetParent(canvasGO.transform, false);
                var text = textGO.AddComponent<TextMeshProUGUI>();
                text.alignment = TextAlignmentOptions.Center;
                text.fontSize = 30;
                text.color = Color.white;
                text.enableAutoSizing = true;
                text.fontStyle = FontStyles.Bold;
                text.outlineColor = Color.black;
                text.outlineWidth = 0.25f;

                RectTransform textRect = text.GetComponent<RectTransform>();
                textRect.anchorMin = Vector2.zero;
                textRect.anchorMax = Vector2.one;
                textRect.offsetMin = new Vector2(10, 10);
                textRect.offsetMax = new Vector2(-10, -10);

                vehiclePopups[id] = text;

                if (!cameraTargetSet)
                {
                    CameraFollow camFollow = Camera.main?.GetComponent<CameraFollow>();
                    if (camFollow != null)
                    {
                        camFollow.target = vehicleObj.transform;
                        cameraTargetSet = true;
                    }
                }
            }

            var obj = vehicleObjects[id];
            obj.transform.position = new Vector3(state.x, verticalOffset, state.y);
            float unityAngle = -(state.angle - 100f);
            Quaternion targetRotation = Quaternion.Euler(0, unityAngle, 0);
            obj.transform.rotation = Quaternion.Slerp(obj.transform.rotation, targetRotation, Time.deltaTime * 10f);
            int clampedPriority = Mathf.Clamp((int)state.priority, 1, 5);
            ApplyPriorityMaterial(obj, clampedPriority);
            if (vehiclePopups.TryGetValue(id, out TextMeshProUGUI popup))
            {
                popup.text = $"Priority: {state.priority}\nCO2: {state.CO2:F1}\nCO: {state.CO:F1}\nHC: {state.HC:F2}\nNOx: {state.NOx:F2}\nPMx: {state.PMx:F2}\nFuel: {state.fuel:F1}";
            }
        }
    }

    void ApplyPriorityMaterial(GameObject vehicleObj, int priority)
    {
        var renderer = vehicleObj.GetComponentInChildren<MeshRenderer>();
        if (renderer != null && priority >= 1 && priority <= 5)
        {
            renderer.material = priorityMaterials[priority - 1];
        }
    }
    void AddPollution(PollutionLevels a, PollutionLevels b)
    {
        a.CO2 += b.CO2;
        a.CO += b.CO;
        a.HC += b.HC;
        a.NOx += b.NOx;
        a.PMx += b.PMx;
    }

    void SubtractPollution(PollutionLevels a, PollutionLevels b)
    {
        a.CO2 -= b.CO2;
        a.CO -= b.CO;
        a.HC -= b.HC;
        a.NOx -= b.NOx;
        a.PMx -= b.PMx;
    }
}