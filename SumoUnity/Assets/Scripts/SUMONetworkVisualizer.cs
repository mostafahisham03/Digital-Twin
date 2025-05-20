using System.Collections.Generic;
using UnityEngine;

[System.Serializable]
public class Position3D
{
    public float x, y, z;
}

[System.Serializable]
public class SumoNode
{
    public string id;
    public Position3D position;
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
    public TextAsset jsonFile;
    public Material laneMaterial;
    public float nodeSize = 1f;
    public bool showNodes = true;

    private Dictionary<string, Vector3> nodePositions = new Dictionary<string, Vector3>();

    void Start()
    {
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

        foreach (var node in network.nodes)
        {
            Vector3 pos = new Vector3(node.position.x, node.position.y, node.position.z);
            nodePositions[node.id] = pos;

            if (showNodes)
            {
                GameObject circle = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                circle.transform.position = pos;
                circle.transform.localScale = new Vector3(nodeSize, 0.01f, nodeSize); // Flattened Y
                circle.name = $"Node_{node.id}";
                circle.transform.parent = transform;

                // Optional: assign lane material for consistency
                if (laneMaterial != null)
                    circle.GetComponent<Renderer>().material = laneMaterial;
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

                    Vector3 midPoint = (start + end) / 2;
                    Vector3 direction = end - start;
                    Vector3 perp = Vector3.Cross(direction.normalized, Vector3.up);

                    float offset = lane.index * lane.width;
                    start += perp * offset;
                    end += perp * offset;

                    GameObject laneSegment = GameObject.CreatePrimitive(PrimitiveType.Cube);
                    laneSegment.transform.position = midPoint;
                    laneSegment.transform.rotation = Quaternion.LookRotation(direction);
                    laneSegment.transform.localScale = new Vector3(lane.width, 0.05f, direction.magnitude);
                    laneSegment.name = $"Lane_{lane.id}_Segment_{i}";
                    laneSegment.transform.parent = edgeGO.transform;

                    if (laneMaterial != null)
                        laneSegment.GetComponent<Renderer>().material = laneMaterial;
                }
            }
        }
    }
}
