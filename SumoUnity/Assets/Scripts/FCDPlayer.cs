using System.Collections.Generic;
using UnityEngine;
using TMPro;
using UnityEngine.UI;

public class FCDPlayer : MonoBehaviour
{
    [Tooltip("FCD output file name inside StreamingAssets")]
    public string fcdFileName = "emission-output.xml";

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
    private Dictionary<string, int> vehiclePriorities = new();

    private FCDParser parser;
    private float simTime = 0f;
    private int currentIndex = 0;

    private bool cameraTargetSet = false;

    private float priorityUpdateInterval = 30f;
    private float priorityTimer = 0f;

    void Start()
    {
        parser = GetComponent<FCDParser>();
        string path = Application.streamingAssetsPath + "/" + fcdFileName;
        parser.LoadFCD(path);
    }

    void Update()
    {
        if (parser.timeSteps.Count == 0) return;

        simTime += Time.deltaTime;
        priorityTimer += Time.deltaTime;

        if (priorityTimer >= priorityUpdateInterval)
        {
            priorityTimer = 0f;
            foreach (var id in vehicleObjects.Keys)
            {
                int newPriority = Random.Range(1, 6);
                vehiclePriorities[id] = newPriority;
                ApplyPriorityMaterial(vehicleObjects[id], newPriority);
            }
        }

        if (currentIndex >= parser.timeSteps.Count) return;

        var step = parser.timeSteps[currentIndex];
        if (simTime >= step.time)
        {
            foreach (var pair in step.vehicles)
            {
                string id = pair.Key;
                var state = pair.Value;

                if (!vehicleObjects.ContainsKey(id))
                {
                    var vehicleObj = Instantiate(vehiclePrefab);
                    vehicleObj.name = $"Vehicle_{id}";
                    vehicleObjects[id] = vehicleObj;

                    int priority = Random.Range(1, 6);
                    vehiclePriorities[id] = priority;
                    ApplyPriorityMaterial(vehicleObj, priority);

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

                    // Background
                    GameObject bgGO = new GameObject("Background");
                    bgGO.transform.SetParent(canvasGO.transform, false);
                    var bgImage = bgGO.AddComponent<Image>();
                    bgImage.color = new Color(0f, 0f, 0f, 0.5f);

                    RectTransform bgRect = bgImage.GetComponent<RectTransform>();
                    bgRect.anchorMin = Vector2.zero;
                    bgRect.anchorMax = Vector2.one;
                    bgRect.offsetMin = Vector2.zero;
                    bgRect.offsetMax = Vector2.zero;

                    // Text
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

                if (vehiclePopups.TryGetValue(id, out TextMeshProUGUI popup))
                {
                    popup.text = $"CO2: {state.CO2:F1}\nCO: {state.CO:F1}\nHC: {state.HC:F2}\nNOx: {state.NOx:F2}\nPMx: {state.PMx:F2}\nFuel: {state.fuel:F1}";
                }
            }
            currentIndex++;
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
}

// Helper to make popup canvas face the camera
public class FaceCamera : MonoBehaviour
{
    void LateUpdate()
    {
        if (Camera.main != null)
        {
            transform.forward = Camera.main.transform.forward;
        }
    }
}
