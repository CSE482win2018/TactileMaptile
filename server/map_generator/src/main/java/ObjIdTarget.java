import static java.awt.Color.WHITE;
import static java.lang.Math.max;
import static java.util.Collections.nCopies;
import static org.osm2world.core.target.common.material.Material.multiplyColor;

import java.awt.Color;
import java.io.PrintStream;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.osm2world.core.map_data.data.MapArea;
import org.osm2world.core.map_data.data.MapElement;
import org.osm2world.core.map_data.data.MapNode;
import org.osm2world.core.map_data.data.MapWaySegment;
import org.osm2world.core.math.TriangleXYZ;
import org.osm2world.core.math.TriangleXYZWithNormals;
import org.osm2world.core.math.VectorXYZ;
import org.osm2world.core.math.VectorXZ;
import org.osm2world.core.osm.data.OSMElement;
import org.osm2world.core.target.common.FaceTarget;
import org.osm2world.core.target.common.TextureData;
import org.osm2world.core.target.common.material.Material;
import org.osm2world.core.target.common.material.Materials;
import org.osm2world.core.world.data.WorldObject;
import org.osm2world.core.target.obj.ObjTarget;

public class ObjIdTarget extends ObjTarget {
  private Class<? extends WorldObject> currentWOGroup;
  private PrintStream objStream;
	private PrintStream mtlStream;

  public ObjIdTarget(PrintStream objStream, PrintStream mtlStream) {
    super(objStream, mtlStream);
		this.objStream = objStream;
    this.mtlStream = mtlStream;
    currentWOGroup = null;
	}

  @Override
  public void beginObject(WorldObject object) {
    if (object == null) {
      currentWOGroup = null;
      objStream.println("g null");
      objStream.println("o null");
    } else {
      if (!object.getClass().equals(currentWOGroup)) {
        currentWOGroup = object.getClass();
        objStream.println("g " + currentWOGroup.getSimpleName());
      }

      MapElement element = object.getPrimaryMapElement();
      OSMElement osmElement;
      if (element instanceof MapNode) {
        osmElement = ((MapNode) element).getOsmNode();
      } else if (element instanceof MapWaySegment) {
        osmElement = ((MapWaySegment) element).getOsmWay();
      } else if (element instanceof MapArea) {
        osmElement = ((MapArea) element).getOsmObject();
      } else {
        osmElement = null;
      }
      
      objStream.println("o " + object.getClass().getSimpleName() + "@" + osmElement.id);
    }
  }
}