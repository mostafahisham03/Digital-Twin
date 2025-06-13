using System.Collections.Generic;
using UnityEngine;

[System.Serializable]
public class Position3D { public float x, y, z; }

[System.Serializable]
public class SumoNode
{
    public string id;
    public Position3D position;
}
[System.Serializable]
public class PollutionLevels
{
    public float CO2;
    public float CO;
    public float HC;
    public float NOx;
    public float PMx;

    public float Total()
    {
        return CO2 + CO + HC + NOx + PMx;
    }
}

[System.Serializable]
public class LaneShapePoint
{
    public float x, y, z;
}

[System.Serializable]
public class Lane
{
    public string id;
    public int index;
    public float width;
    public List<LaneShapePoint> shape;
}

[System.Serializable]
public class SumoEdge
{
    public string id;
    public string from, to;
    public List<Lane> lanes;
}

[System.Serializable]
public class SumoNetwork
{
    public List<SumoNode> nodes;
    public List<SumoEdge> edges;
}

public class SUMONetworkVisualizer : MonoBehaviour
{
    [Header("Network Input")]
    public TextAsset jsonFile;
    public Material laneMaterial;

    [Header("Display Settings")]
    public float nodeSize = 1f;
    public bool showNodes = true;

    [Header("Pollution Regions")]
    public bool showPollutionRegionsOnNodes = false;
    public bool showPollutionRegionsOnLanes = true;
    public float pollutionTileSize = 200f;
    public float PollutionThreshold = 3000f;

    private Gradient pollutionGradient;
    private Dictionary<string, Vector3> nodePositions = new();
    private List<Vector3> pollutionPoints = new();
    private Dictionary<Vector2Int, float> tileCOValues = new();
    private Dictionary<Vector2Int, PollutionLevels> tilePollutionValues = new();


    private float minX, minZ;

    void Start()
    {
        InitializePollutionGradient();

        if (jsonFile == null)
        {
            Debug.LogError("Assign a JSON file first.");
            return;
        }

        var network = JsonUtility.FromJson<SumoNetwork>(jsonFile.text);
        if (network == null || network.nodes == null || network.edges == null)
        {
            Debug.LogError("Malformed or empty JSON.");
            return;
        }

        System.Random rand = new();

        minX = float.MaxValue;
        minZ = float.MaxValue;
        float maxX = float.MinValue;
        float maxZ = float.MinValue;

        foreach (var node in network.nodes)
        {
            Vector3 pos = new Vector3(node.position.x, node.position.y, node.position.z);
            nodePositions[node.id] = pos;

            minX = Mathf.Min(minX, pos.x);
            minZ = Mathf.Min(minZ, pos.z);
            maxX = Mathf.Max(maxX, pos.x);
            maxZ = Mathf.Max(maxZ, pos.z);
        }

        foreach (var node in network.nodes)
        {
            Vector3 pos = nodePositions[node.id];

            if (showNodes)
            {
                GameObject circle = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                circle.transform.position = pos;
                circle.transform.localScale = new Vector3(nodeSize, 0.01f, nodeSize);
                circle.name = $"Node_{node.id}";
                circle.transform.parent = transform;

                if (laneMaterial != null)
                    circle.GetComponent<Renderer>().material = laneMaterial;
            }

            if (showPollutionRegionsOnNodes)
            {
                pollutionPoints.Add(pos);
            }
        }

        foreach (var edge in network.edges)
        {
            GameObject edgeGO = new GameObject($"Edge_{edge.id}");
            edgeGO.transform.parent = transform;

            if (edge.lanes == null) continue;

            foreach (var lane in edge.lanes)
            {
                if (lane.shape == null || lane.shape.Count < 2) continue;

                for (int i = 0; i < lane.shape.Count - 1; i++)
                {
                    Vector3 start = new Vector3(lane.shape[i].x, lane.shape[i].y, lane.shape[i].z);
                    Vector3 end = new Vector3(lane.shape[i + 1].x, lane.shape[i + 1].y, lane.shape[i + 1].z);

                    Vector3 direction = end - start;
                    Vector3 perp = Vector3.Cross(direction.normalized, Vector3.up);
                    float offset = lane.index * lane.width;
                    start += perp * offset;
                    end += perp * offset;

                    GameObject laneSegment = GameObject.CreatePrimitive(PrimitiveType.Cube);
                    laneSegment.transform.position = (start + end) / 2;
                    laneSegment.transform.rotation = Quaternion.LookRotation(direction);
                    laneSegment.transform.localScale = new Vector3(lane.width, 0.05f, direction.magnitude);
                    laneSegment.name = $"Lane_{lane.id}_Segment_{i}";
                    laneSegment.transform.parent = edgeGO.transform;

                    if (laneMaterial != null)
                        laneSegment.GetComponent<Renderer>().material = laneMaterial;

                    if (showPollutionRegionsOnLanes)
                    {
                        pollutionPoints.Add(start);
                    }
                }
            }
        }

        InitializeTilesBasePollution(rand);
        GeneratePollutionTiles();
    }

    void InitializePollutionGradient()
    {
        pollutionGradient = new Gradient();
        pollutionGradient.SetKeys(
            new GradientColorKey[] {
                new GradientColorKey(Color.green, 0f),
                new GradientColorKey(Color.yellow, 0.5f),
                new GradientColorKey(Color.red, 1f)
            },
            new GradientAlphaKey[] {
                new GradientAlphaKey(0.3f, 0f),
                new GradientAlphaKey(0.3f, 1f)
            }
        );
    }

    void InitializeTilesBasePollution(System.Random rand)
    {
        tileCOValues.Clear();

        foreach (var pt in pollutionPoints)
        {
            int tileX = Mathf.FloorToInt((pt.x - minX) / pollutionTileSize);
            int tileZ = Mathf.FloorToInt((pt.z - minZ) / pollutionTileSize);
            Vector2Int tileCoord = new(tileX, tileZ);

            if (!tileCOValues.ContainsKey(tileCoord))
            {
                PollutionLevels basePollution = new PollutionLevels
                {
                    CO2 = 400f + (float)(rand.NextDouble() * 100f),
                    CO = 100f + (float)(rand.NextDouble() * 150f),
                    HC = 20f + (float)(rand.NextDouble() * 50f),
                    NOx = 0f + (float)(rand.NextDouble() * 20f),
                    PMx = 15f + (float)(rand.NextDouble() * 150f),
                };
                tilePollutionValues[tileCoord] = basePollution;
                tileCOValues[tileCoord] = basePollution.Total();
            }
        }
    }

    public void UpdatePollutionWithVehicleLevels(Dictionary<Vector3, PollutionLevels> vehiclePollutionLevels)
    {
        if (vehiclePollutionLevels == null || vehiclePollutionLevels.Count == 0) return;

        foreach (var kvp in vehiclePollutionLevels)
        {
            Vector3 vehiclePos = kvp.Key;
            PollutionLevels vehiclePollution = kvp.Value;

            int tileX = Mathf.FloorToInt((vehiclePos.x - minX) / pollutionTileSize);
            int tileZ = Mathf.FloorToInt((vehiclePos.z - minZ) / pollutionTileSize);
            Vector2Int tileCoord = new(tileX, tileZ);

            if (tilePollutionValues.ContainsKey(tileCoord))
            {
                tilePollutionValues[tileCoord].CO2 += vehiclePollution.CO2;
                tilePollutionValues[tileCoord].CO += vehiclePollution.CO;
                tilePollutionValues[tileCoord].HC += vehiclePollution.HC;
                tilePollutionValues[tileCoord].NOx += vehiclePollution.NOx;
                tilePollutionValues[tileCoord].PMx += vehiclePollution.PMx;
            }
            else
            {
                tilePollutionValues[tileCoord] = vehiclePollution;
            }
        }


        RefreshPollutionTiles();
    }
    public float MinX => minX;
    public float MinZ => minZ;

    // Apply CO deltas to tiles (+ or -)
    public void ApplyTilePollutionChanges(Dictionary<Vector2Int, PollutionLevels> tilePollutionChanges)
    {
        foreach (var kvp in tilePollutionChanges)
        {
            if (tilePollutionValues.ContainsKey(kvp.Key))
            {
                tilePollutionValues[kvp.Key].CO2 += kvp.Value.CO2;
                tilePollutionValues[kvp.Key].CO += kvp.Value.CO;
                tilePollutionValues[kvp.Key].HC += kvp.Value.HC;
                tilePollutionValues[kvp.Key].NOx += kvp.Value.NOx;
                tilePollutionValues[kvp.Key].PMx += kvp.Value.PMx;
            }
            else
            {
                tilePollutionValues[kvp.Key] = kvp.Value;
            }
        }

        RefreshPollutionTiles();
    }


    void GeneratePollutionTiles()
    {
        int tileIndex = 0;
        foreach (var kvp in tilePollutionValues)
        {
            Vector3 center = new Vector3(
                minX + kvp.Key.x * pollutionTileSize + pollutionTileSize / 2,
                0.05f,
                minZ + kvp.Key.y * pollutionTileSize + pollutionTileSize / 2
            );

            float totalPollution = kvp.Value.Total();
            CreatePollutionTile(kvp.Key, center, totalPollution, tileIndex++);
        }

    }

    void RefreshPollutionTiles()
    {
        List<GameObject> toDestroy = new();

        foreach (Transform child in transform)
        {
            if (child.name.StartsWith("PollutionTile_") || child.name.StartsWith("COText_"))
            {
                toDestroy.Add(child.gameObject);
            }
        }

        foreach (var go in toDestroy)
        {
            Destroy(go);
        }

        GeneratePollutionTiles();
    }

    void CreatePollutionTile(Vector2Int tileCoord, Vector3 center, float totalPollutionValue, int tileIndex)
    {
        float percent = Mathf.Clamp01(totalPollutionValue / PollutionThreshold);
        Color tileColor = pollutionGradient.Evaluate(percent);

        GameObject tile = GameObject.CreatePrimitive(PrimitiveType.Cube);
        tile.transform.position = center;
        tile.transform.localScale = new Vector3(pollutionTileSize, 0.2f, pollutionTileSize);
        tile.name = $"PollutionTile_{tileIndex}";
        tile.transform.parent = transform;

        var mat = new Material(Shader.Find("Standard"));
        mat.color = tileColor;
        mat.SetFloat("_Mode", 3);
        mat.SetInt("_SrcBlend", (int)UnityEngine.Rendering.BlendMode.SrcAlpha);
        mat.SetInt("_DstBlend", (int)UnityEngine.Rendering.BlendMode.OneMinusSrcAlpha);
        mat.SetInt("_ZWrite", 0);
        mat.DisableKeyword("_ALPHATEST_ON");
        mat.EnableKeyword("_ALPHABLEND_ON");
        mat.DisableKeyword("_ALPHAPREMULTIPLY_ON");
        mat.renderQueue = 3000;

        tile.GetComponent<Renderer>().material = mat;

        GameObject textGO = new GameObject($"COText_{tileIndex}");
        textGO.transform.position = center + new Vector3(0, 2f, 0);
        textGO.transform.parent = tile.transform;

        var textMesh = textGO.AddComponent<TextMesh>();
        textMesh.text = $"{(percent * 100f):F1}% Pollution";
        textMesh.fontSize = 80;
        textMesh.characterSize = 0.7f;
        textMesh.color = Color.black;
        textMesh.alignment = TextAlignment.Center;
        textMesh.anchor = TextAnchor.MiddleCenter;
    }
}
