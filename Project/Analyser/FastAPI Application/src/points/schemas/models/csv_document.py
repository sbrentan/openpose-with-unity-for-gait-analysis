import csv
import os
from datetime import datetime
from typing import List

from sqlmodel import SQLModel, Field

import global_variables
from points.schemas.models.body import BodyPart, SkeletonParts
from points.settings import DOCUMENTS_FOLDER


class CSVDocument(SQLModel, table=True):
    id: int = Field(primary_key=True, index=True)
    name: str
    file_name: str = Field(alias="fileName")
    created_at: datetime = Field(default=datetime.now(), alias="createdAt")

    @property
    def skeletons(self) -> List[SkeletonParts]:
        if self.id in global_variables.point_variables.document_skeletons:
            return global_variables.point_variables.document_skeletons[self.id]
        else:
            if self.id not in global_variables.point_variables.document_skeletons:
                skeleton_list = []
                document_path = os.path.join(DOCUMENTS_FOLDER, self.file_name)
                with open(document_path, newline='', encoding='utf-8') as csvfile:
                    csv_reader = csv.reader(csvfile)
                    skeleton = None
                    for row_num, row in enumerate(csv_reader):
                        if row_num == 0:
                            continue
                        row_id = int(row[1])
                        if not skeleton or row_id != skeleton.id:
                            if skeleton:
                                skeleton_list.append(skeleton)
                            skeleton = SkeletonParts(**{
                                "id": int(row[1]),
                                "datetime": row[2],
                                "parts": []
                            })
                        skeleton.parts.append(BodyPart(**{
                            "part_type": row[3],
                            "x": float(row[4]),
                            "y": float(row[5]),
                            "skeleton_id": row_id
                        }))
                    skeleton_list.append(skeleton)
                global_variables.point_variables.document_skeletons[self.id] = skeleton_list
            else:
                skeleton_list = global_variables.point_variables.document_skeletons[self.id]
            return skeleton_list
