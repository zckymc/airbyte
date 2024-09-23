/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.data.AirbyteType
import io.airbyte.cdk.data.JsonDecoder
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LeafAirbyteType
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.discover.AirbyteStreamFactory
import io.airbyte.cdk.discover.CdcIntegerMetaFieldType
import io.airbyte.cdk.discover.CdcStringMetaFieldType
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.JdbcAirbyteStreamFactory
import io.airbyte.cdk.discover.LosslessFieldType
import io.airbyte.cdk.discover.MetaField
import io.airbyte.protocol.models.v0.AirbyteStream
import io.micronaut.context.annotation.Primary
import java.time.OffsetDateTime
import javax.inject.Singleton

@Singleton
@Primary
class MysqlJdbcStreamFactory(val base: JdbcAirbyteStreamFactory) : AirbyteStreamFactory by base {
    @Override
    override fun createGlobal(discoveredStream: DiscoveredStream): AirbyteStream {
        val mysqlGlobalStream = base.createGlobal(discoveredStream)
        mysqlGlobalStream.apply {
            (jsonSchema["properties"] as ObjectNode).apply {
                for (metaField in MysqlCDCMetaFields.entries) {
                    set<ObjectNode>(metaField.id, metaField.type.airbyteType.asJsonSchema())
                }
            }
        }
        return mysqlGlobalStream
    }

    enum class MysqlCDCMetaFields(
        override val type: FieldType,
    ) : MetaField {
        CDC_LOG_POS(CdcIntegerMetaFieldType),
        CDC_LOG_FILE(CdcStringMetaFieldType),
        ;

        override val id: String
            get() = MetaField.META_PREFIX + name.lowercase()
    }

    data object CdcOffsetDateTimeMetaFieldType : LosslessFieldType {
        override val airbyteType: AirbyteType = LeafAirbyteType.TIMESTAMP_WITH_TIMEZONE
        override val jsonEncoder: JsonEncoder<OffsetDateTime> = OffsetDateTimeCodec
        override val jsonDecoder: JsonDecoder<OffsetDateTime> = OffsetDateTimeCodec
    }
}
